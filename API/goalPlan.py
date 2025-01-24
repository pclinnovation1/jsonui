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
COLLECTION_NAME = CONFIG["mongodb"]["API_goal_plan"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

CONFIGURATION_MAPPING_GOAL_PLANS = {
    "goal_plan_name": "GoalPlanName",
    "description": "Description",
    "enable_weighting_flag": "EnableWeightingFlag",
    "end_date": "EndDate",
    "evaluation_type": "EvaluationType",
    "goal_access_level_code": "GoalAccessLevelCode",
    "goal_plan_active_code": "GoalPlanActiveCode",
    "primary_goal_plan_flag": "PrimaryGoalPlanFlag",
    "start_date": "StartDate",
    "evaluation_type_meaning": "EvaluationTypeMeaning",
    "goal_access_level_meaning": "GoalAccessLevelMeaning",
    "goal_plan_active_code_meaning": "GoalPlanActiveCodeMeaning",
    "assignees": "Assignees",
    "nbr_of_pd_consumed": "NbrOfPDConsumed",
}

def map_goal_plans_data(goal_plan_item):
    """Map API response fields to MongoDB document fields."""
    mapped_data = {key: goal_plan_item.get(value, None) for key, value in CONFIGURATION_MAPPING_GOAL_PLANS.items()}
    return mapped_data

def fetch_goal_plans():
    """Fetch goal plans from the API."""
    goal_plans_data = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_goal_plans_chunk(offset):
        """Fetch a chunk of goal plans."""
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/goalPlans?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_goal_plans_chunk, offset) for offset in offsets]):
            goal_plans_data.extend(future.result())

    return goal_plans_data

def generate_report3():
    """Generate and store goal plans report."""
    try:
        goal_plans = fetch_goal_plans()
        mapped_data = [map_goal_plans_data(goal_plan) for goal_plan in goal_plans]

        if mapped_data:
            collection.insert_many(mapped_data)
            message = f"Inserted {len(mapped_data)} goal plan records successfully."
        else:
            message = "No goal plan records found."
        print(message)
        return message

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return f"Error fetching data: {e}"
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}"
