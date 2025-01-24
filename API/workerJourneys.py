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
COLLECTION_NAME = CONFIG["mongodb"]["API_workerJourneys"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Configuration for worker journeys mapping
CONFIGURATION_MAPPING_WORKER_JOURNEY = {
    "category": "Category",
    "instance": "Instance",
    "name": "Name",
    "journey_display_name": "JourneyDisplayName",
    "country_code": "CountryCode",
    "person_number": "PersonNumber",  # Updated field for person number
    "status": "Status",
    "allocation_date": "AllocationDate",
    "completion_date": "CompletionDate",
    "archive_offset_days": "ArchiveOffsetDays",
    "purge_offset_days": "PurgeOffsetDays",
    "completion_criteria": "CompletionCriteria",
    "completion_offset_days": "CompletionOffsetDays"
}

# Function to map worker journey data with Person Number
def map_worker_journey_data(worker_journey_item, person_mapping):
    mapped_data = {key: worker_journey_item.get(value, None) for key, value in CONFIGURATION_MAPPING_WORKER_JOURNEY.items()}
    person_id = worker_journey_item.get("PersonId")
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

def fetch_worker_journeys():
    worker_journeys = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_workersj_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/workerJourneys?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_workersj_chunk, offset) for offset in offsets]):
            worker_journeys.extend(future.result())

    return worker_journeys

def generate_report3():
    """Route to fetch and return worker journey data."""
    try:
        # Fetch person ID to person number mapping
        person_mapping = fetch_person_id_to_number_mapping()

        # Fetch worker journeys data
        worker_journeys_data = fetch_worker_journeys()

        mapped_data = []

        # Map worker journeys data using the fetched person mapping
        for journey in worker_journeys_data:
            mapped_data.append(map_worker_journey_data(journey, person_mapping))

        # If mapped data is not empty, insert it into MongoDB
        if mapped_data:
            collection.insert_many(mapped_data)
            message = f"Inserted {len(mapped_data)} worker journey records successfully."
        else:
            message = "No worker journey records found."

        print(message)
        return message    

    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching data: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

