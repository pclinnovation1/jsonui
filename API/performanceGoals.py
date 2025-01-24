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
COLLECTION_NAME = CONFIG["mongodb"]["API_performance_goals"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

CONFIGURATION_MAPPING_PERFORMANCE_GOALS = {
    "goal_name": "GoalName",
    "person_number": "PersonNumber",
    "description": "Description",
    "goal_start_date": "StartDate",
    "status": "Status",
    "target_completion_date": "TargetCompletionDate",
    "status_meaning": "StatusMeaning",
    "percent_complete": "PercentComplete"
}

def map_performance_goals_data(goal_item):
    mapped_data = {key: goal_item.get(value, None) for key, value in CONFIGURATION_MAPPING_PERFORMANCE_GOALS.items()}
    return mapped_data

def fetch_performance_goals():
    performance_goals_data = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_performance_goals_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/performanceGoals?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_performance_goals_chunk, offset) for offset in offsets]):
            performance_goals_data.extend(future.result())

    return performance_goals_data

def generate_report3():
    try:
        performance_goals = fetch_performance_goals()
        mapped_data =[map_performance_goals_data(goal) for goal in performance_goals]

        if mapped_data:
            collection.insert_many(mapped_data)
            message = f"Inserted {len(mapped_data)} performance goals records successfully."
        else:
            message = "No performance goals records found."
        print(message)
        return message

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return f"Error fetching data: {e}"
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}"

