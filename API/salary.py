import requests
import concurrent.futures
from datetime import datetime, MINYEAR
from flask import Flask, jsonify
from pymongo import MongoClient
import warnings
import json
import re

# Flask App initialization
app = Flask(__name__)

# Load configuration file
with open("config.json", "r") as config_file:
    CONFIG = json.load(config_file)

# MongoDB Configuration
MONGODB_URI = CONFIG["mongodb"]["uri"]
DATABASE_NAME = CONFIG["mongodb"]["database_name"]
COLLECTION_NAME = CONFIG["mongodb"]["API_salary"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Configurations
CONFIGURATION_MAPPING_EMP = {
    "person_id": "PersonId",
    "person_name": "DisplayName",
    "person_number": "PersonNumber"
}

CONFIGURATION_MAPPING_SALARY = {
    "currency": "CurrencyCode",
    "salary_effective_date": "DateFrom",
    "base_salary": "SalaryAmount",
    "person_number": "PersonNumber",
    "person_name": "PersonDisplayName",
    "salary_frequency_code": "SalaryFrequencyCode",
    "salary_basis_type": "SalaryBasisType",
    "salary_end_date": "DateTo",
    "adjustment_amount": "AdjustmentAmount",
    "adjustment_percentage": "AdjustmentPercentage",
    "annual_salary": "AnnualSalary",
    "annual_full_time_salary": "AnnualFullTimeSalary",
    "quartile": "Quartile",
    "quintile": "Quintile",
    "compa_ratio": "CompaRatio",
    "range_position": "RangePosition",
    "salary_range_minimum": "SalaryRangeMinimum",
    "salary_range_midpoint": "SalaryRangeMidPoint",
    "salary_range_maximum": "SalaryRangeMaximum",
    "frequency_name": "FrequencyName",
    "code": "Code",
    "legal_employer_name": "LegalEmployerName",
    "grade_ladder_name": "GradeLadderName",
    "grade_name": "GradeName",
    "grade_step_name": "GradeStepName",
    "geography_name": "GeographyName",
    "geography_type_name": "GeographyTypeName",
    "fte": "FTEValue",
    "next_salary_review_date": "NextSalReviewDate",
    "salary_basis_name": "SalaryBasisName",
    "amount_decimal_precision": "AmountDecimalPrecision",
    "salary_amount_scale": "SalaryAmountScale",
    "amount_rounding_code": "AmountRoundingCode",
    "annual_rounding_code": "AnnualRoundingCode",
    "range_rounding_code": "RangeRoundingCode",
    "work_at_home": "WorkAtHome",
    "quartile_meaning": "QuartileMeaning",
    "quintile_meaning": "QuintileMeaning",
    "has_future_salary": "hasFutureSalary",
    "multiple_components": "MultipleComponents",
    "component_usage": "ComponentUsage",
    "pending_transaction_exists": "PendingTransactionExists",
    "range_error_warning": "RangeErrorWarning",
    "payroll_factor": "PayrollFactor",
    "salary_factor": "SalaryFactor",
    "payroll_frequency_code": "PayrollFrequencyCode",
    "salary_transaction_status": "SalaryTransactionStatus"
}

CONFIGURATION_MAPPING_ASSIGNMENTS = {
    "assignment_id": "AssignmentId",
    "effective_start_date": "EffectiveStartDate",
    "effective_end_date": "EffectiveEndDate",
}

# Function to map data
def map_data(data, config):
    return {key: data.get(value, None) for key, value in config.items()}

def map_assignment_data(data):
    """
    Map the assignment data and fetch the one with the latest EffectiveStartDate.
    """
    latest_assignment = None
    latest_work_relationship = None
    latest_start_date = datetime.min

    for work_relationship in data.get("workRelationships", []):
        for assignment in work_relationship.get("assignments", []):
            start_date_str = assignment.get("EffectiveStartDate")
            
            # Check for missing or invalid dates
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                except ValueError:
                    # Skip this assignment if date is invalid
                    print(f"Invalid date format: {start_date_str}")
                    continue

                # Compare to find the latest date
                if start_date > latest_start_date:
                    latest_start_date = start_date
                    latest_work_relationship = work_relationship
                    latest_assignment = assignment
            else:
                print("Missing EffectiveStartDate in assignment.")
    
    # Map work relationship data and assignment data
    if latest_assignment and latest_work_relationship:

        assignment_data = map_data(latest_assignment, CONFIGURATION_MAPPING_ASSIGNMENTS)

        # Combine data
        return {**assignment_data}

    return {}

def map_employee_data(data):
    """
    Map the employee data to the configuration.
    """
    return {key: data.get(value, None) for key, value in CONFIGURATION_MAPPING_EMP.items()}

# Function to map data to configuration
def map_data_to_configuration(data, config):
    return {key: data.get(value, None) for key, value in config.items()}

# Function to fetch latest salary for assignment IDs
def fetch_latest_salary_for_assignments(assignment_ids):
    total_salaries = []
    fetched_assignment_ids = set()  # To track which assignment IDs returned salaries
    missing_assignment_ids = set()  # To track missing assignment IDs
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch(assignment_id):
        url = f'{api_config['url']}/hcmRestApi/resources/11.13.18.05/salaries?limit={api_config['limit']}&expand=all&onlyData=true&q=AssignmentId="{assignment_id}"'
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    # Fetch salaries concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch, assignment_id): assignment_id for assignment_id in assignment_ids}
        for future in concurrent.futures.as_completed(futures):
            assignment_id = futures[future]
            try:
                result = future.result()
                if result:  # Salaries returned
                    total_salaries.extend(result)
                    fetched_assignment_ids.add(assignment_id)
                else:
                    missing_assignment_ids.add(assignment_id)
            except Exception as e:
                print(f"Failed to fetch salary for Assignment ID {assignment_id}: {e}")
                missing_assignment_ids.add(assignment_id)

    # Process salaries to find the latest one for each assignment
    latest_salaries = {}
    for salary in total_salaries:
        assignment_id = salary.get("AssignmentId")
        if assignment_id:
            date_from = datetime.strptime(salary["DateFrom"], "%Y-%m-%d")
            # Compare and store the latest salary based on "DateFrom"
            if assignment_id not in latest_salaries or date_from > datetime.strptime(latest_salaries[assignment_id]["salary_effective_date"], "%Y-%m-%d"):
                latest_salaries[assignment_id] = map_data_to_configuration(salary, CONFIGURATION_MAPPING_SALARY)

    # Print missing assignment IDs
    if missing_assignment_ids:
        print(f"Missing Assignment IDs: {missing_assignment_ids}")
        print(f"Total missing salaries: {len(missing_assignment_ids)}")

    return latest_salaries

# Fetch worker data with work relationships and assignments
def fetch_workers_with_assignments():
    total_data = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_worker_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/workers?limit={api_config['limit']}&offset={offset}&expand=workRelationships.assignments&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_worker_chunk, offset) for offset in offsets]):
            total_data.extend(future.result())

    return total_data

# Process worker data and extract latest assignment only
def process_worker_data(workers_data):
    combined_data = []

    for worker in workers_data:
        # Process work relationships
        work_relationships = worker.get("workRelationships", [])    
        # Map the latest assignment
        latest_assignment = map_assignment_data({"workRelationships": work_relationships})
        # Create a flattened document with employee, work_relationship, and latest_assignment
        combined_data.append({
            **latest_assignment  # Add latest assignment
        })

    return combined_data

# Generate report
def generate_report3():
    try:
        # Step 1: Fetch workers data
        workers_data = fetch_workers_with_assignments()
        print(f"Fetched {len(workers_data)} workers.")
    
        # Step 2: Process and map data
        processed_data = process_worker_data(workers_data)
        print(f"Processed {len(processed_data)} records with latest assignments.")
        

        # Step 2: Extract assignment IDs
        assignment_ids = [emp["assignment_id"] for emp in processed_data if emp.get("assignment_id")]
        print(f"Extracted {len(assignment_ids)} assignment IDs")


        # Step 3: Fetch latest salaries
        latest_salaries = fetch_latest_salary_for_assignments(assignment_ids)
        print(f"Fetched {len(latest_salaries)} latest salaries")

        # Combine employee data with latest salaries
        for emp in processed_data:
            assignment_id = emp.get("assignment_id")
            if assignment_id and assignment_id in latest_salaries:
                emp.update(latest_salaries[assignment_id])

        # Keys to exclude
        keys_to_exclude = {"assignment_id", "effective_start_date", "effective_end_date", "person_id"}

        # Filter out the keys from processed data
        def filter_excluded_keys(data):
            return {key: value for key, value in data.items() if key not in keys_to_exclude}

        # Filter processed data before writing to the file
        filtered_data = [filter_excluded_keys(emp) for emp in processed_data]
        
        # Step 3: Insert into MongoDB
        if filtered_data:
            collection.insert_many(filtered_data)
            print(f"Inserted {len(filtered_data)} records into MongoDB.")

        return f"{len(processed_data)} worker records with latest assignments inserted successfully."
       
        
    except requests.RequestException as e:
        print(f"Error during API call: {e}")
        return "Failed to generate report due to API error."
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Failed to generate report due to an internal error."
