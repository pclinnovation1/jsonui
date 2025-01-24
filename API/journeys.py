import json
import requests
import concurrent.futures
from flask import Flask
from pymongo import MongoClient


# Flask App initialization
app = Flask(__name__)

# Load configuration file
with open("config.json", "r") as config_file:
    CONFIG = json.load(config_file)

# MongoDB Configuration
MONGODB_URI = CONFIG["mongodb"]["uri"]
DATABASE_NAME = CONFIG["mongodb"]["database_name"]
COLLECTION_NAME = CONFIG["mongodb"]["API_journeys"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

CONFIGURATION_MAPPING_JOURNEYS = {
    "level": "Level",
    "level_value": "LevelValue",
    "category": "Category",
    "sub_category": "SubCategory",
    "name": "Name",
    "code": "Code",
    "country_code": "CountryCode"
}

def map_journeys_data(journey_item):
    """Map API response fields to MongoDB document fields."""
    mapped_data = {key: journey_item.get(value, None) for key, value in CONFIGURATION_MAPPING_JOURNEYS.items()}
    return mapped_data

def fetch_journeys():
    """Fetch journeys from the API."""
    journeys_data = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_journeys_chunk(offset):
        """Fetch a chunk of journeys."""
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/journeys?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_journeys_chunk, offset) for offset in offsets]):
            journeys_data.extend(future.result())

    return journeys_data

def generate_report3():
    """Generate and store journeys report."""
    try:
        journeys = fetch_journeys()
        mapped_data = [map_journeys_data(journey) for journey in journeys]

        if mapped_data:
            collection.insert_many(mapped_data)
            message = f"Inserted {len(mapped_data)} journeys records successfully."
        else:
            message = "No journeys records found."
        print(message)
        return message

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return f"Error fetching data: {e}"
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}"
