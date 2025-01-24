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
COLLECTION_NAME = CONFIG["mongodb"]["API_eligible_options_lov"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

CONFIGURATION_MAPPING_ELIGIBLE_OPTIONS = {
    "component_name": "ComponentName",
    "start_date": "StartDate",
    "end_date": "EndDate",
    "start_date_code": "StartDateCode",
    "end_date_code": "EndDateCode",
    "start_date_rule": "StartDateRule",
    "end_date_rule": "EndDateRule",
    "person_number": "PersonNumber",
    "effective_date": "EffectiveDate",
    "assignment_number": "AssignmentNumber",
    "pool_id_to_consume": "PoolIdToConsume",
    "input_currency_code": "InputCurrencyCode",
    "processing_type": "ProcessingType",
    "multiple_entries_allowed_flag": "MultipleEntriesAllowedFlag",
    "requires_attachment": "RequiresAttachment",
    "non_monetary_uom": "NonMonetaryUOM",
    "grant_type": "GrantType",
    "trading_symbol": "TradingSymbol"
}

def map_eligible_options_data(option_item,person_mapping):
    mapped_data = {key: option_item.get(value, None) for key, value in CONFIGURATION_MAPPING_ELIGIBLE_OPTIONS.items()}
    person_id = option_item.get("PersonId")
    mapped_data["person_number"] = person_mapping.get(person_id)  # Add person number from the mapping
    return mapped_data

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

def fetch_eligible_options():
    eligible_options_data = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_eligible_options_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/eligibleOptionsLOV?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_eligible_options_chunk, offset) for offset in offsets]):
            eligible_options_data.extend(future.result())

    return eligible_options_data

def generate_report3():
    try:
        # Fetch person ID to person number mapping
        person_mapping = fetch_person_id_to_number_mapping()

        eligible_options = fetch_eligible_options()

        mapped_data = []
        
        # Map worker journeys data using the fetched person mapping
        for options in eligible_options:
            mapped_data.append(map_eligible_options_data(options, person_mapping))

        if mapped_data:
            collection.insert_many(mapped_data)
            message = f"Inserted {len(mapped_data)} eligible options records successfully."
        else:
            message = "No eligible options records found."

        print(message)
        return message

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return jsonify({"error": f"Error fetching data: {e}"}), 500
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": f"An error occurred: {e}"}), 500
