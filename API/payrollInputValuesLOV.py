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
COLLECTION_NAME = CONFIG["mongodb"]["API_payrollInputValuesLOV"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Function to map payrollInputValuesLOV data
CONFIGURATION_MAPPING_PAYROLL_INPUT_VALUES = {
    "effective_start_date": "EffectiveStartDate",
    "effective_end_date": "EffectiveEndDate",
    "input_value_name": "InputValueName",
    "display_sequence": "DisplaySequence",
    "uom": "UOM",
    "reserved_input_value": "ReservedInputValue",
    "element_name": "ElementName",
    "element_effective_start_date": "ElementEffectiveStartDate",
    "element_effective_end_date": "ElementEffectiveEndDate",
    "legislative_data_group_name": "LegislativeDataGroupName",
    "legislation_code": "LegislationCode"
}

def map_payroll_input_values_data(input_value_item):
    return {key: input_value_item.get(value, None) for key, value in CONFIGURATION_MAPPING_PAYROLL_INPUT_VALUES.items()}

# Function to fetch payrollInputValuesLOV data
def fetch_payroll_input_values():
    payroll_input_values = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_payroll_input_values_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/payrollInputValuesLOV?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_payroll_input_values_chunk, offset) for offset in offsets]):
            payroll_input_values.extend(future.result())

    return payroll_input_values

def generate_report3():
    try:
        # Fetch payrollInputValuesLOV data
        payroll_input_values_data = fetch_payroll_input_values()

        mapped_data = []
        
        # Map payrollInputValuesLOV data
        for input_value in payroll_input_values_data:
            mapped_data.append(map_payroll_input_values_data(input_value))

        # If mapped data is not empty, insert it into MongoDB
        if mapped_data:
            collection.insert_many(mapped_data)
            message = f"Inserted {len(mapped_data)} payroll input values records successfully."
        else:
            message = "No payroll input values records found."

        print(message)
        return message

    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching data: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
