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
COLLECTION_NAME = CONFIG["mongodb"]["API_payrollTimeDefinitionsLOV"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Function to map payrollTimeDefinitionsLOV data
CONFIGURATION_MAPPING_PAYROLL_TIME_DEFINITIONS = {
    "definition_type": "DefinitionType",
    "definition_name": "DefinitionName",
    "name": "Name"
}

def map_payroll_time_definitions_data(time_definition_item):
    return {key: time_definition_item.get(value, None) for key, value in CONFIGURATION_MAPPING_PAYROLL_TIME_DEFINITIONS.items()}

# Function to fetch payrollTimeDefinitionsLOV data
def fetch_payroll_time_definitions():
    payroll_time_definitions = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_payroll_time_definitions_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/payrollTimeDefinitionsLOV?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_payroll_time_definitions_chunk, offset) for offset in offsets]):
            payroll_time_definitions.extend(future.result())

    return payroll_time_definitions

def generate_report3():
    try:
        # Fetch payrollTimeDefinitionsLOV data
        payroll_time_definitions_data = fetch_payroll_time_definitions()

        mapped_data = []
        
        # Map payrollTimeDefinitionsLOV data
        for time_definition in payroll_time_definitions_data:
            mapped_data.append(map_payroll_time_definitions_data(time_definition))

        # If mapped data is not empty, insert it into MongoDB
        if mapped_data:
            collection.insert_many(mapped_data)
            message = f"Inserted {len(mapped_data)} payroll time definitions records successfully."
        else:
            message = "No payroll time definitions records found."

        print(message)
        return message

    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching data: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
