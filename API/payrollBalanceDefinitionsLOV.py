import json
import requests
from flask import Flask, jsonify
from pymongo import MongoClient
import concurrent.futures

# Flask App initialization
app = Flask(__name__)

# Load configuration file
with open("config.json", "r") as config_file:
    CONFIG = json.load(config_file)

# MongoDB Configuration
MONGODB_URI = CONFIG["mongodb"]["uri"]
DATABASE_NAME = CONFIG["mongodb"]["database_name"]
COLLECTION_NAME = CONFIG["mongodb"]["API_payrollBalanceDefinitionsLOV"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Function to map payrollBalanceDefinitionsLOV data
CONFIGURATION_MAPPING_PAYROLL_BALANCE_DEFINITIONS = {
    "base_balance_name": "BaseBalanceName",
    "balance_name": "BalanceName",
    "reporting_name": "ReportingName",
    "legislation_code": "LegislationCode",
    "user_category_name": "UserCategoryName",
    "legislative_data_group_name": "LegislativeDataGroupName"
}

def map_payroll_balance_definitions_data(balance_definition_item):
    return {key: balance_definition_item.get(value, None) for key, value in CONFIGURATION_MAPPING_PAYROLL_BALANCE_DEFINITIONS.items()}

# Function to fetch payrollBalanceDefinitionsLOV data
def fetch_payroll_balance_definitions():
    payroll_balance_definitions = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_payroll_balance_definitions_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/payrollBalanceDefinitionsLOV?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_payroll_balance_definitions_chunk, offset) for offset in offsets]):
            payroll_balance_definitions.extend(future.result())

    return payroll_balance_definitions

def generate_report3():
    try:
        # Fetch payrollBalanceDefinitionsLOV data
        payroll_balance_definitions_data = fetch_payroll_balance_definitions()

        mapped_data = []
        

        # Map payrollBalanceDefinitionsLOV data
        for balance_definition in payroll_balance_definitions_data:
            mapped_balance_definition_data = map_payroll_balance_definitions_data(balance_definition)
            mapped_data.append(mapped_balance_definition_data)

        # If mapped data is not empty, insert it into MongoDB
        if mapped_data:
            collection.insert_many(mapped_data)
            message = f"Inserted {len(mapped_data)} payroll balance definitions records successfully."
        else:
            message = "No payroll balance definitions records found."

        print(message)
        return jsonify({"message": message}), 200

    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching data: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
