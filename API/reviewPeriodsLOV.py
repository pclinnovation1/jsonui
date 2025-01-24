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

# Configuration mapping for Review Periods LOV
CONFIGURATION_MAPPING_REVIEW_PERIODS_LOV = {
    "review_period_id": "ReviewPeriodId",
    "review_period_name": "ReviewPeriodName",
    "start_date": "StartDate",
    "end_date": "EndDate",
    "status_code": "StatusCode"
}

# Function to map Review Periods LOV data
def map_review_periods_data(review_period_item):
    return {key: review_period_item.get(value, None) for key, value in CONFIGURATION_MAPPING_REVIEW_PERIODS_LOV.items()}

# Function to fetch Review Periods LOV data
def fetch_review_periods_lov():
    review_periods = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_review_periods_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/reviewPeriodsLOV?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_review_periods_chunk, offset) for offset in offsets]):
            review_periods.extend(future.result())

    return review_periods

# Route to fetch and handle Review Periods LOV data
@app.route('/api/reviewPeriodsLOV', methods=['GET'])
def generate_review_periods_lov_report():
    """Route to fetch and return review periods LOV data."""
    try:
        # Fetch review periods LOV data
        review_periods_data = fetch_review_periods_lov()

        mapped_data = []

        # Map review periods LOV data
        for review_period in review_periods_data:
            mapped_data.append(map_review_periods_data(review_period))

        # If mapped data is not empty, insert it into MongoDB
        if mapped_data:
            collection.insert_many(mapped_data)
            message = f"Inserted {len(mapped_data)} review period records successfully."
        else:
            message = "No review period records found."

        print(message)
        return jsonify({"message": message}), 200

    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching data: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
