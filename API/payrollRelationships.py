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
COLLECTION_NAME = CONFIG["mongodb"]["API_payrollRelationships"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Function to map payrollRelationships data
CONFIGURATION_MAPPING_PAYROLL_RELATIONSHIPS = {
    "payroll_relationship_number": "PayrollRelationshipNumber",
    "start_date": "StartDate",
    "end_date": "EndDate",
    "country": "Country",
    "party_number": "PartyNumber",
    "effective_end_date": "EffectiveEndDate",
    "effective_start_date": "EffectiveStartDate",
    "person_number": "PersonNumber"
}

def map_payroll_relationships_data(relationship_item):
    return {key: relationship_item.get(value, None) for key, value in CONFIGURATION_MAPPING_PAYROLL_RELATIONSHIPS.items()}

# Function to fetch payrollRelationships data
def fetch_payroll_relationships():
    payroll_relationships = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_payroll_relationships_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/payrollRelationships?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_payroll_relationships_chunk, offset) for offset in offsets]):
            payroll_relationships.extend(future.result())

    return payroll_relationships

def generate_report3():
    try:
        # Fetch payrollRelationships data
        payroll_relationships_data = fetch_payroll_relationships()

        mapped_data = []
        
        # Map payrollRelationships data
        for relationship in payroll_relationships_data:
            mapped_data.append(map_payroll_relationships_data(relationship))

        # If mapped data is not empty, insert it into MongoDB
        if mapped_data:
            collection.insert_many(mapped_data)
            message = f"Inserted {len(mapped_data)} payroll relationships records successfully."
        else:
            message = "No payroll relationships records found."

        print(message)
        return message

    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching data: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
