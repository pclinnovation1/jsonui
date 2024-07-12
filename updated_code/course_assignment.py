import re
from pymongo import MongoClient
from datetime import datetime, timedelta
import dateparser
from word2number import w2n

# Define the MongoDB connection and database
def get_mongo_connection():
    return MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')

# Function to extract numbers and time units from text
def extract_time_units(text):
    pattern = re.compile(r'(\d+|\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\b)\s*(day|week|month|year)s?\s*(before|after)?', re.IGNORECASE)
    matches = pattern.findall(text)
    return matches

# Function to parse due date from extracted numbers and time units
def parse_due_date(start_date, text):
    time_units = extract_time_units(text)
    due_date = start_date

    for number_word, number_digit, unit, direction in time_units:
        number = int(number_word) if number_word.isdigit() else w2n.word_to_num(number_word.lower())
        if unit.lower() == 'day':
            delta = timedelta(days=number)
        elif unit.lower() == 'week':
            delta = timedelta(weeks=number)
        elif unit.lower() == 'month':
            delta = dateparser.parse(f"in {number} months", settings={'RELATIVE_BASE': due_date}) - due_date
        elif unit.lower() == 'year':
            delta = dateparser.parse(f"in {number} years", settings={'RELATIVE_BASE': due_date}) - due_date

        if direction and direction.lower() == 'before':
            due_date -= delta
        else:
            due_date += delta
    return due_date

def find_employee_by_person_number(db, person_number):
    employee_collection = db['S_EmployeeDetails_UK']
    employee = employee_collection.find_one({'Person_Number': person_number})
    if employee:
        print(f"Employee found: {employee}")
    else:
        print(f"No employee found with Person_Number: {person_number}")
    return employee

# assign_course_to_employee when job code changes 

def assign_courses():  
    client = get_mongo_connection()
    db = client['PCL_Interns']
    employee_collection = db['S_EmployeeDetails_UK']
    job_jobfamily_collection = db['Job_JobFamily']
    course_jobfamily_collection = db['Course_Job_family']
    course_rules_collection = db['S_CourseRules']
    courses_assigned_collection = db['S_CourseAssignments']

    now = datetime.now()
    twenty_four_hours_ago = now - timedelta(hours=24)

    # Fetch employees whose Effective Start Date is within the last 24 hours
    employees = list(employee_collection.find({'Effective_Start_Date': {'$gte': twenty_four_hours_ago}}))
    
    if not employees:
        print("No employee data found in the past 24 hours.")
        return "No employee data found"

    for employee in employees:
        if employee.get('Effective_End_Date') is not None:
            continue

        person_number = employee['Person_Number']
        person_name = employee['First_Name'] + ' ' + employee['Last_Name']
        new_job_code = employee['Job_Code']
        old_record = find_employee_by_person_number(db, person_number)
        
        if old_record and old_record['Job_Code'] != new_job_code:
            job_family_entry = job_jobfamily_collection.find_one({'JOB': new_job_code})
            if job_family_entry:
                job_family = job_family_entry['JOB FAMILY']
                print(job_family)
                courses = list(course_jobfamily_collection.find({' JOB FAMILY ': job_family}))
                print(courses)

                for course in courses:
                    print(course['COURSE'])
                    course_details = course_rules_collection.find_one({'Course_Name': course['COURSE']})
                    print(course_details)
                    if course_details and 'Rule1' in course_details:
                        due_date = parse_due_date(now, course_details['Rule1'])
                        assign_course_to_employee(courses_assigned_collection, person_number, person_name, course_details['Course_Name'], due_date)
                        
    return "Completed"

def assign_course_to_employee(courses_assigned_collection, person_number, person_name, course_name, due_date):
    # Format due_date to exclude time
    due_date_str = due_date.strftime('%Y-%m-%d')
    courses_assigned_collection.insert_one({
        'Person_Number': person_number,
        'Person_Name': person_name,
        'Course_Name': course_name,
        'Assigned_Date': datetime.now().strftime('%Y-%m-%d'),
        'Due_Date': due_date_str,
        'Completion_Date': None,
        'Timestamp': datetime.now()
    })
    print(f"Assigned {course_name} to employee {person_number} with due date {due_date_str}")

if __name__ == '__main__':
    assign_courses()
