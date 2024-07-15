import re
import logging
from datetime import datetime, timedelta
from pymongo import MongoClient, errors, DESCENDING
import dateparser
from word2number import w2n

# MongoDB connection setup
def get_mongo_connection():
    client = MongoClient("mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns")  # Update this with your MongoDB connection string
    db = client["PCL_Interns"]
    return db

# Function to convert ISO format string to datetime.date
def from_iso_date(date_str):
    return datetime.fromisoformat(date_str).date() if date_str else None

# Function to extract numbers and time units from text
def extract_time_units(text):
    pattern = re.compile(r'(\d+|\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\b)\s*(day|week|month|year)s?\s*(before|after)?', re.IGNORECASE)
    matches = pattern.findall(text)
    return matches

# Function to parse due date from extracted numbers and time units
def parse_due_date(start_date, time_units):
    if isinstance(start_date, datetime):
        due_date = start_date
    else:
        due_date = datetime(start_date.year, start_date.month, start_date.day)

    for match in time_units:
        number_word, number_digit, unit, direction = match
        number = int(number_word) if number_word.isdigit() else w2n.word_to_num(number_word)
        if unit.lower() == 'day':
            delta = timedelta(days=number)
        elif unit.lower() == 'week':
            delta = timedelta(weeks=number)
        elif unit.lower() == 'month':
            delta = dateparser.parse(f"in {number} months", settings={'RELATIVE_BASE': due_date}) - due_date
        elif unit.lower() == 'year':
            delta = dateparser.parse(f"in {number} years", settings={'RELATIVE_BASE': due_date}) - due_date

        if direction.lower() == 'before':
            due_date -= delta
        else:
            due_date += delta
    return due_date

# Reassignment cycle for mandatory learning
reassignment_cycle = {
    "GDPR": 1,  # January
    "Modern Slavery": 3,  # March
    "Health & Safety Essentials": 4,  # April
    "Cyber Security": 5,  # May
    "Safeguarding Children": 6,  # June
    "Fire Safety": 9,  # September
    "Diversity & Inclusion": 10,  # October
    "Safeguarding Adults": 11  # November
}

def get_last_day_of_month(year, month):
    if month == 12:
        return datetime(year, 12, 31)
    return datetime(year, month + 1, 1) - timedelta(days=1)

def reassign_courses(params,db):
    db = get_mongo_connection()
    courses_collection = db["Mandatory_Learning_Courses"]
    employees_collection = db["EmployeeDetails_UK"]
    
    # Set specific date for "today" to the first day of the current month
    today = datetime(datetime.now().year, datetime.now().month, 1)

    # Fetch employee name from params
    if "Employee_Name" not in params:
        return "Missing Employee_Name parameter."
    employee_name = params["Employee_Name"]

    # Find the employee by name
    name_parts = employee_name.split()
    if len(name_parts) < 2:
        return "Invalid Employee_Name. Please provide both first and last names."
    first_name = name_parts[0]
    last_name = name_parts[1]
    
    employee = employees_collection.find_one({"First_Name": first_name, "Last_Name": last_name})
    if not employee:
        return "Employee not found"

    person_number = employee["Person_Number"]
    reassigned_courses = []
    completed_this_year = []

    for course, month_index in reassignment_cycle.items():
        reassignment_date = today.replace(month=month_index, day=1)
        due_date = get_last_day_of_month(reassignment_date.year, reassignment_date.month)

        # Only process the reassignment if the specific date matches the course's reassignment month
        if today.month == month_index:
            # Check if the course was completed in the previous year
            last_course = courses_collection.find_one({
                "Person_Number": person_number,
                "Course_Name": course
            }, sort=[("Due_Date", DESCENDING)])

            # Check if the course was assigned in the current year
            assigned_this_year = courses_collection.find_one({
                "Person_Number": person_number,
                "Course_Name": course,
                "Assigned_Date": {"$gte": datetime(today.year, 1, 1)}
            })

            if last_course and not assigned_this_year:
                courses_collection.insert_one({
                    "Person_Number": person_number,
                    "Course_Name": course,
                    "Assigned_Date": reassignment_date.strftime("%Y-%m-%d"),
                    "Due_Date": due_date.strftime("%Y-%m-%d"),
                    "Status": "Assigned"
                })
                reassigned_courses.append(course)
            else:
                completed_this_year.append(course)

    if reassigned_courses:
        return f"The following courses have been reassigned to you: {', '.join(reassigned_courses)}"
    else:
        return "All mandatory courses were completed this year. They will be reassigned next year."

if __name__ == "__main__":
    params = {"Employee_Name": input("Enter the Employee Name: ")}
    message = reassign_courses(params)
    print(message)
