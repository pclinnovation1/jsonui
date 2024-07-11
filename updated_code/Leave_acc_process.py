from flask import Flask
from pymongo import MongoClient
from bson import ObjectId
from wrapper_Leave_Acc import update_or_insert_leave_accrual
import datetime

app = Flask(__name__)

# MongoDB client setup
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')  # Adjust the connection string as necessary
db = client['PCL_Interns']  # Database name
employee_collection = db['S_EmployeeDetails_UK']  # Employee details collection
process_details_collection = db['Process_Details']  # Ensure this collection is defined

# Function to find person number based on the population filters
def find_person_number(population_filters):
    query = {}

    # Handle the "person" field if present
    if 'person' in population_filters and isinstance(population_filters['person'], str) and population_filters['person'].strip():
        person_name = population_filters['person'].strip()
        if ' ' in person_name:
            first_name, last_name = person_name.split(' ', 1)
            query['First_Name'] = first_name
            query['Last_Name'] = last_name
        else:
            query['First_Name'] = person_name

    # Add other filters to the query
    for key, value in population_filters.items():
        if key != 'person':
            if key == 'business_unit' and value.strip():
                query['BusinessUnit'] = value.strip()
            elif key == 'legal_employer' and value.strip():
                query['LegalEmployer'] = value.strip()
            elif isinstance(value, str) and value.strip():
                query[key] = value.strip()
            else:
                print(f"Skipping key {key} with non-string value {value} of type {type(value)}")

    # Only pick records where Effective_End_Date is null or in the future
    query["$or"] = [{"Effective_End_Date": None}, {"Effective_End_Date": {"$gte": datetime.datetime.now()}}]

    print(f"Constructed Query: {query}")

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

        try:
            # Update status to Running
            process_details_collection.update_one(
                {'_id': process_details_id},  # Use process_details_id directly
                {'$set': {'Status': 'Running'}}
            )
            print(f"Population Filters JSON: {population_filters}")

            # Ensure population_filters is a dictionary
            if not isinstance(population_filters, dict):
                raise ValueError("population_filters should be a dictionary")

            # Validate and log each key and value in population_filters
            for key, value in population_filters.items():
                if isinstance(value, dict):
                    print(f"Value for key {key} is a nested dictionary: {value}")
                elif isinstance(value, list):
                    print(f"Value for key {key} is a list: {value}")
                elif isinstance(value, str):
                    print(f"Value for key {key} is a string: {value}")
                else:
                    print(f"Value for key {key} is of type {type(value)}: {value}")

            matching_person_numbers = find_person_number(population_filters)
            print(f"Matching Person Numbers: {matching_person_numbers}")

            if not matching_person_numbers:
                raise Exception("No matching person numbers found.")

            # Process each matching person number
            results = []
            for person_number in matching_person_numbers:
                result = update_or_insert_leave_accrual(person_number)
                results.append(result)

            print(f"Results: {results}")
            return "Completed" if all(results) else "Partial Success"

        except Exception as e:
            process_details_collection.update_one(
                {'_id': process_details_id},
                {'$set': {'Status': 'Failed', 'Error': str(e)}}
            )
            print(f"Error: {str(e)}")
            return "Failed"

if __name__ == "__main__":
    # Example population filters for debugging
    population_filters = {
        "person": "Jane Smith",
        "business_unit": "HR",
        "legal_employer": "XYZ Corp"
    }

    # Create a mock process details entry for debugging
    process_details_id = process_details_collection.insert_one({
        "Status": "Pending",
        "Created_At": datetime.datetime.now(),
        "Population_Filters": population_filters
    }).inserted_id

    # Run Leave_acc_main function for debugging
    status = Leave_acc_main(population_filters, process_details_id, db)
    print(f"Leave_acc_main completed with status: {status}")

    # Start the Flask app
    app.run(debug=True)
