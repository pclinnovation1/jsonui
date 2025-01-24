import json
import requests
import concurrent.futures
from flask import Flask, jsonify
from pymongo import MongoClient

# Flask App initialization
app = Flask(__name__)

# Load configuration file
with open("config.json", "r") as config_file:
    CONFIG = json.load(config_file)

# MongoDB Configuration
MONGODB_URI = CONFIG["mongodb"]["uri"]
DATABASE_NAME = CONFIG["mongodb"]["database_name"]
COLLECTION_NAME = CONFIG["mongodb"]["API_absence_plan_balances"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

CONFIGURATION_MAPPING_PLAN_BALANCES = {
    "plan_name": "planName",
    "plan_type": "planType",
    "plan_status": "planStatus",
    "plan_status_meaning": "planStatusMeaning",
    "plan_display_status_flag": "planDisplayStatusFlag",
    "enrollment_start_date": "enrollmentStartDate",
    "enrollment_end_date": "enrollmentEndDate",
    "balance_as_of_balance_calculation_date": "balanceAsOfBalanceCalculationDate",
    "balance_calculation_date": "balanceCalculationDate",
    "plan_unit_of_measure": "planUnitOfMeasure",
    "unit_of_measure_meaning": "unitOfMeasureMeaning",
    "enroll_positive_balance_flag": "enrollPositiveBalanceFlag",
    "plan_type_code": "planTypeCode",
    "ceiling_amount": "ceilingAmount",
    "effective_start_date": "effectiveStartDate",
    "effective_end_date": "effectiveEndDate",
    "level": "level",
    "plan_enrollment_status": "planEnrollmentStatus",
    "assignment_name": "assignmentName",
    "assignment_number": "assignmentNumber",
    "formatted_balance": "formattedBalance",
    "plan_period_start_date": "planPeriodStartDate",
    "plan_period_end_date": "planPeriodEndDate",
    "formatted_ceiling_amount": "formattedCeilingAmount",
    "recipient_alias_name": "recipientAliasName",
    "multi_year_carry_over_flag": "multiYearCarryOverFlag",
    "sys_effective_date": "SysEffectiveDate",
    "transfer_rule": "transferRule"
}

# Function to fetch Person ID to Person Number mapping
def fetch_person_id_to_number_mapping():
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    person_mapping = {}

    # Function to fetch a chunk of worker data
    def fetch_workers_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/workers?fields=PersonId,PersonNumber&limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    # Use ThreadPoolExecutor to fetch worker data in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_workers_chunk, offset) for offset in offsets]):
            workers = future.result()
            for worker in workers:
                person_mapping[worker["PersonId"]] = worker["PersonNumber"]

    return person_mapping


# Function to map plan balances data with Person Number
def map_plan_balances_data(plan_item, person_mapping):
    mapped_data = {key: plan_item.get(value, None) for key, value in CONFIGURATION_MAPPING_PLAN_BALANCES.items()}
    # Add Person Number
    person_id = plan_item.get("personId")
    mapped_data["person_number"] = person_mapping.get(person_id)
    return mapped_data

# Function to fetch plan balances data
def fetch_plan_balances_data():
    plan_balances_data = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))
    print("person_mapping")
    # Fetch Person ID to Person Number mapping
    person_mapping = fetch_person_id_to_number_mapping()
    print("fetch balance")
    def fetch_plan_balances_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/planBalances?limit={api_config['limit']}&offset={offset}&onlyData=true"
        print(f"DEBUG: Fetching chunk with offset {offset}...")
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        print("this done2")
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_plan_balances_chunk, offset) for offset in offsets]):
            plan_balances_data.extend(future.result())
            print(f"DEBUG: Current total plan balances fetched: {len(plan_balances_data)}")
            print("this done1")
    print("this done")
    # Map and enrich data
    return [map_plan_balances_data(plan, person_mapping) for plan in plan_balances_data]

# Function to generate report and insert into MongoDB
def generate_report3():
    try:
        # Fetch plan balances data
        plan_balances_data = fetch_plan_balances_data()
        # Insert merged data into MongoDB
        collection.insert_many(plan_balances_data)
        message = f"Inserted {len(plan_balances_data)} plan balance records successfully."
        print(message)
        return message

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return f"Error fetching data: {e}"
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}"
