import re
from flask import Flask, request, jsonify
from pymongo import MongoClient, errors
from datetime import datetime, timedelta
from word2number import w2n
import dateparser
import logging
import pymongo

app = Flask(__name__)

# MongoDB connection setup
def get_mongo_connection():
    client = MongoClient("mongodb://localhost:27017/")  # Update this with your MongoDB connection string
    db = client["company2"]
    return db

# Function to convert date to ISO format string
def to_iso_date(date):
    return date.date().isoformat()

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

def assign_courses(employee):
    db = get_mongo_connection()
    courses_collection = db["Mandatory_Learning_Courses"]
    hire_date = datetime.strptime(employee["Hire_Date"], "%Y-%m-%d")
    due_date = hire_date + timedelta(days=45)

    courses = ["GDPR", "Modern Slavery", "Health & Safety Essentials", "Cyber Security",
               "Safeguarding Children", "Fire Safety", "Diversity & Inclusion", "Safeguarding Adults"]

    for course in courses:
        courses_collection.insert_one({
            "Person_Number": employee["Person_Number"],
            "Course_Name": course,
            "Assigned_Date": hire_date.strftime("%Y-%m-%d"),
            "Due_Date": due_date.strftime("%Y-%m-%d"),
            "Status": "Assigned"
        })

    return "Courses assigned successfully."

def get_last_day_of_month(year, month):
    if month == 12:
        return datetime(year, 12, 31)
    return datetime(year, month + 1, 1) - timedelta(days=1)

def reassign_courses(employee_name):
    db = get_mongo_connection()
    courses_collection = db["Mandatory_Learning_Courses"]
    employees_collection = db["EmployeeDetails_UK"]
    
    # Set specific date for "today" to the first day of the current month
    today = datetime(datetime.now().year, datetime.now().month, 1)

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
            }, sort=[("Due_Date", pymongo.DESCENDING)])

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

@app.route('/assignExistingEmployeeCourse', methods=['POST'])
def assign_existing_employee_course():
    data = request.json
    if not data or "Employee_Name" not in data or "Course_Name" not in data:
        return jsonify({"error": "Missing Employee_Name or Course_Name in request body"}), 400

    employee_name = data["Employee_Name"]
    course_name = data["Course_Name"]

    db = get_mongo_connection()
    employees_collection = db["EmployeeDetails_UK"]
    courses_collection = db["CourseAssignments"]
    course_rules_collection = db["CourseRules"]

    # Find the employee by name
    name_parts = employee_name.split()
    if len(name_parts) < 2:
        return jsonify({"error": "Invalid Employee_Name. Please provide both first and last names."}), 400
    first_name = name_parts[0]
    last_name = name_parts[1]
    
    employee = employees_collection.find_one({"First_Name": first_name, "Last_Name": last_name})
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    person_number = employee["Person_Number"]
    
    # Check if the course exists in the rules collection
    course_rule = course_rules_collection.find_one({"Course Name": course_name})
    if not course_rule:
        return jsonify({"error": "Course not found in rules collection"}), 404

    # Check if the employee is already assigned to the course
    existing_assignment = courses_collection.find_one({
        "Person_Number": person_number,
        "Course_Name": course_name
    }, sort=[("Due_Date", pymongo.DESCENDING)])

    if existing_assignment:
        if "Completion_Date" in existing_assignment and existing_assignment["Completion_Date"]:
            original_completion_date = from_iso_date(existing_assignment["Completion_Date"])
            rule2_text = course_rule.get("Rule2", "")
            time_units_due_date = extract_time_units(rule2_text)
            reassignment_due_date = parse_due_date(original_completion_date, time_units_due_date)
            if datetime.now().date() < reassignment_due_date.date():
                return jsonify({"error": "Cannot reassign before the reassignment due date"}), 400

    # Calculate dates based on rules
    date_assignment = datetime.now().date()
    rule1_text = course_rule.get("Rule1", "")
    time_units_due_date = extract_time_units(rule1_text)
    due_date = parse_due_date(date_assignment, time_units_due_date)
    due_date_str = due_date.date()
    completion_date = None

    # Create the new assignment in the required format
    new_assignment = {
        "Person_Number": person_number,
        "Person_Name": employee_name,
        "Course_Name": course_name,
        "Assigned_Date": date_assignment.isoformat(),
        "Due_Date": due_date_str.isoformat(),
        "Completion_Date": completion_date,
        "Timestamp": datetime.now()
    }

    try:
        result = courses_collection.insert_one(new_assignment)
        new_assignment["_id"] = str(result.inserted_id)
        return jsonify(new_assignment), 201
    except errors.PyMongoError as e:
        logging.error(f"Error inserting data: {e}")
        return jsonify({"error": f"Error inserting data: {e}"}), 500

@app.route('/hireEmployee', methods=['POST'])
def hire_employee():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    db = get_mongo_connection()
    employees_collection = db["EmployeeDetails_UK"]

    try:
        employee_id = employees_collection.insert_one(data).inserted_id
        employee = employees_collection.find_one({"_id": employee_id})
        assign_courses(employee)
        return jsonify({"message": "Employee hired and courses assigned successfully."}), 200
    except errors.PyMongoError as e:
        logging.error(f"Error inserting data: {e}")
        return jsonify({"error": f"Error inserting data: {e}"}), 500

@app.route('/reassignCourses', methods=['POST'])
def reassign_courses_endpoint():
    data = request.json
    if not data or "Employee_Name" not in data:
        return jsonify({"error": "Missing Employee_Name in request body"}), 400

    employee_name = data["Employee_Name"]
    
    try:
        message = reassign_courses(employee_name)
        return jsonify({"message": message}), 200
    except errors.PyMongoError as e:
        logging.error(f"Error during reassignment: {e}")
        return jsonify({"error": f"Error during reassignment: {e}"}), 500

@app.route('/viewCourses', methods=['POST'])
def view_courses():
    data = request.json
    if not data or "Employee_Name" not in data:
        return jsonify({"error": "Missing Employee_Name in request body"}), 400

    employee_name = data["Employee_Name"]

    db = get_mongo_connection()
    employees_collection = db["EmployeeDetails_UK"]
    courses_collection = db["S_CourseAssignments"]

    try:
        # Find the employee's person number using their name
        name_parts = employee_name.split()
        if len(name_parts) < 2:
            return jsonify({"error": "Invalid Employee_Name. Please provide both first and last names."}), 400
        first_name = name_parts[0]
        last_name = name_parts[1]
        
        employee_record = employees_collection.find_one({"First_Name": first_name, "Last_Name": last_name})
        if not employee_record:
            return jsonify({"error": "No employee found with the specified name"}), 404

        person_number = employee_record["Person_Number"]

        # Find courses for the employee using their person number
        records = courses_collection.find({"Person_Number": person_number})
        courses = []
        for record in records:
            courses.append({
                "Course_Name": record["Course_Name"],
                "Assigned_Date": record["Date_Assignment"],
                "Due_Date": record["Due_Date"],
                "Status": record.get("Status", "Assigned")
            })

        if not courses:
            return jsonify({"error": "No courses found for the specified employee"}), 404

        return jsonify({"employee_name": employee_name, "courses": courses}), 200
    except errors.PyMongoError as e:
        logging.error(f"Error retrieving data: {e}")
        return jsonify({"error": f"Error retrieving data: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
