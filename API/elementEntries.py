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
COLLECTION_NAME = CONFIG["mongodb"]["API_elementEntries"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Configuration mapping for Element Entries
CONFIGURATION_MAPPING_ELEMENT_ENTRIES = {
    "effective_start_date": "EffectiveStartDate",
    "effective_end_date": "EffectiveEndDate",
    "creator_type": "CreatorType",
    "entry_type": "EntryType",
    "entry_sequence": "EntrySequence",
    "reason": "Reason",
    "subpriority": "Subpriority",
    "person_number": "PersonNumber",
    "assignment_number": "AssignmentNumber",
    "payroll_relationship_number": "PayrollRelationshipNumber",
    "element_name": "ElementName",
    "usage_level": "UsageLevel",
    "intent": "Intent"
}

# Function to map Element Entries data
def map_element_entries_data(element_entry_item):
    return {key: element_entry_item.get(value, None) for key, value in CONFIGURATION_MAPPING_ELEMENT_ENTRIES.items()}

# Function to fetch Element Entries data
def fetch_element_entries():
    element_entries = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_element_entries_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/elementEntries?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_element_entries_chunk, offset) for offset in offsets]):
            element_entries.extend(future.result())

    return element_entries

def generate_report3():
    """Route to fetch and return element entries data."""
    try:
        # Fetch element entries data
        element_entries_data = fetch_element_entries()

        mapped_data = []

        # Map element entries data
        for element_entry in element_entries_data:
            mapped_data.append(map_element_entries_data(element_entry))

        # If mapped data is not empty, insert it into MongoDB
        if mapped_data:
            collection.insert_many(mapped_data)
            message = f"Inserted {len(mapped_data)} element entries records successfully."
        else:
            message = "No element entries records found."

        print(message)
        return message

    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching data: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
