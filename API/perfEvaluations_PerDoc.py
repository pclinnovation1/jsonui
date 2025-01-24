import json
import requests
import concurrent.futures
from flask import Flask, jsonify
from pymongo import MongoClient
import re


# Flask App initialization
app = Flask(__name__)

# Load configuration file
with open("config.json", "r") as config_file:
    CONFIG = json.load(config_file)

# MongoDB Configuration
MONGODB_URI = CONFIG["mongodb"]["uri"]
DATABASE_NAME = CONFIG["mongodb"]["database_name"]
COLLECTION_NAME = CONFIG["mongodb"]["API_perfEvaluations_PerDoc"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]


# Configuration mapping for Performance Evaluations
CONFIGURATION_MAPPING_PERFORMANCE_EVALUATIONS = {
    "person_number": "PersonNumber",
    "performance_document_name": "PerformanceDocumentName",
    "name": "Name",
    "start_date": "StartDate",
    "end_date": "EndDate",
    "status_code": "StatusCode",
    "template_type_code": "TemplateTypeCode",
    "eval_status": "EvalStatus"
}

def map_performance_evaluations_data(evaluation_item):
    """Map API response fields to MongoDB document fields."""
    mapped_data = {key: evaluation_item.get(value, None) for key, value in CONFIGURATION_MAPPING_PERFORMANCE_EVALUATIONS.items()}
    return mapped_data

def fetch_performance_evaluations():
    """Fetch performance evaluations from the API."""
    performance_evaluations_data = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_performance_evaluations_chunk(offset):
        """Fetch a chunk of performance evaluations."""
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/performanceEvaluations?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_performance_evaluations_chunk, offset) for offset in offsets]):
            performance_evaluations_data.extend(future.result())

    return performance_evaluations_data

def generate_report3():
    """Generate and store performance evaluations report."""
    try:
        performance_evaluations = fetch_performance_evaluations()
        mapped_data = [map_performance_evaluations_data(evaluation) for evaluation in performance_evaluations]

        if mapped_data:
            collection.insert_many(mapped_data)
            message = f"Inserted {len(mapped_data)} performance evaluations records successfully."
        else:
            message = "No performance evaluations records found."
        print(message)
        return message

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return f"Error fetching data: {e}"
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}"
