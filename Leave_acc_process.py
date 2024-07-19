from flask import Flask
from pymongo import MongoClient
from wrapper_Leave_Acc import update_or_insert_leave_accrual

app = Flask(__name__)

# MongoDB client setup
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')  # Adjust the connection string as necessary
db = client['PCL_Interns']  # Database name
employee_collection = db['S_EmployeeDetails_UK']  # Employee details collection

# Function to find person number based on the population filters
def find_person_number(population_filters):
    query = {}

    # Handle the "Person" field if present
    if 'Person' in population_filters and population_filters['Person'].strip():
        person_name = population_filters['Person'].strip()
        if ' ' in person_name:
            first_name, last_name = person_name.split(' ', 1)
            query['First_Name'] = first_name
            query['Last_Name'] = last_name
        else:
            query['First_Name'] = person_name

    # Add other filters to the query
    for key, value in population_filters.items():
        if key != 'Person' and value.strip():
            query[key] = value.strip()

    # Only pick records where Effective_End_Date is null
    query["Effective_End_Date"] = None

    # Execute the query
    matching_persons = []
    all_records = employee_collection.find(query)

    for record in all_records:
        if "Person_Number" in record:
            matching_persons.append(record["Person_Number"])

    return matching_persons

# Leave_acc_main function to be called with population filters
def Leave_acc_main(population_filters, process_details_id, db):
    with app.app_context():
        process_details_collection = db['Process_Details']
        
        # Update status to Running
        process_details_collection.update_one(
            {'_id': process_details_id},  # Use process_details_id directly
            {'$set': {'Status': 'Running'}}
        )
        print(f"Population Filters JSON: {population_filters}")

        matching_person_numbers = find_person_number(population_filters)
        print(f"Matching Person Numbers: {matching_person_numbers}")

        # Process each matching person number
        results = []
        for person_number in matching_person_numbers:
            result = update_or_insert_leave_accrual(person_number)
            results.append(result)

        print(f"Results: {results}")
        return results

# # Example of how the scheduler might call this function
# if __name__ == "__main__":
#     import sys
#     import json

#     # Expecting JSON input as a command-line argument
#     if len(sys.argv) != 2:
#         print("Usage: python script.py '<population_filters_json>'")
#         sys.exit(1)

#     # Parse the JSON input
#     population_filters_json = sys.argv[1]
#     try:
#         population_filters = json.loads(population_filters_json)
#     except json.JSONDecodeError:
#         print("Invalid JSON input")
#         sys.exit(1)

#     # Call the Leave_acc_main function with the provided JSON
#     Leave_acc_main(population_filters)
