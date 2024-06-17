import re
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
import dateparser
from word2number import w2n

# Define the MongoDB connection and database
def get_mongo_connection():
    return MongoClient("mongodb://localhost:27017/")

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
    # Ensure start_date is a datetime object
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

# Function to check and renew course assignments within a date range
def check_and_renew_courses(db_name, rules_collection_name, assignments_collection_name, from_date, to_date):
    # Connect to MongoDB
    db = get_mongo_connection()[db_name]
    rules_collection = db[rules_collection_name]
    assignments_collection = db[assignments_collection_name]

    # Fetch all course assignments
    assignments = assignments_collection.find()

    for assignment in assignments:
        person = assignment['Person']
        course_name = assignment['Course_Name']
        completion_date_str = assignment.get('Completion_Date')

        if completion_date_str:
            completion_date = from_iso_date(completion_date_str)
        else:
            print(f"No completion date for course {course_name} for {person}")
            continue

        print(course_name)

        # Fetch the course rules from the rules collection
        course_rule = rules_collection.find_one({"Course_Name": course_name})
        print(course_rule)

        if course_rule:
            # Extract the rules
            rule2 = course_rule.get('Rule2', '')
            rule3 = course_rule.get('Rule3', '')

            # Extract time units from rule2
            time_units_due_date = extract_time_units(rule2)
            print(time_units_due_date)
            if not time_units_due_date:
                continue  # Skip if the rule is not applicable

            # Calculate the due date based on rule2
            due_date = parse_due_date(completion_date, time_units_due_date)
            print(due_date)

            # Extract time units from rule3 for auto-assign date
            time_units_auto_assign = extract_time_units(rule3)
            print(time_units_auto_assign)
            if not time_units_auto_assign:
                continue  # Skip if the rule is not applicable

            # Calculate the auto-assign date based on rule3
            auto_assign_date = parse_due_date(due_date, time_units_auto_assign)

            # Check if auto-assign date is within the given date range
            print(auto_assign_date)
            if from_date <= auto_assign_date.date() <= to_date:
                # Update the existing assignment
                new_date_assignment = auto_assign_date
                new_due_date = new_date_assignment + timedelta(days=90)

                update_result = assignments_collection.update_one(
                    {"Person": person, "Course_Name": course_name},
                    {
                        "$set": {
                            "Date_Assignment": to_iso_date(new_date_assignment),
                            "Due_Date": to_iso_date(new_due_date),
                            "Completion_Date": None,  # Not yet completed
                            "timestamp" : datetime.now()
                        }
                    }
                )
                if update_result.matched_count > 0:
                    print(f"Updated course '{course_name}' for {person} with new due date {new_due_date}")
                else:
                    print(f"No matching assignment found to update for {person} and course '{course_name}'")

# Example usage
db_name = 'company2'
rules_collection_name = 'CourseRules'
assignments_collection_name = 'CourseAssignments'
from_date = datetime(2024, 10, 1).date()
to_date = datetime(2024, 12, 31).date()
check_and_renew_courses(db_name, rules_collection_name, assignments_collection_name, from_date, to_date)