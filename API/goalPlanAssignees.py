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
COLLECTION_NAME = CONFIG["mongodb"]["API_goal_plan_assignees"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

CONFIGURATION_MAPPING_GOAL_PLAN_ASSIGNEES = {
    "goal_plan_name": "GoalPlanName",
    "department": "DepartmentName",
    "assignment_name": "AssignmentName",
    "assignment_number": "AssignmentNumber",
    "person_name": "DisplayName",
    "person_number": "PersonNumber",
    "job_name": "JobName",
    "position_name": "PositionName",
    "location_name": "LocationName",
    "business_unit": "BusinessUnitName",
    "manager_name": "ManagerName"
}

def map_goal_plan_assignees_data(assignee_item):
    """Map API response fields to MongoDB document fields."""
    mapped_data = {key: assignee_item.get(value, None) for key, value in CONFIGURATION_MAPPING_GOAL_PLAN_ASSIGNEES.items()}
    return mapped_data

def fetch_goal_plan_assignees():
    """Fetch goal plan assignees from the API."""
    goal_plan_assignees_data = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_goal_plan_assignees_chunk(offset):
        """Fetch a chunk of goal plan assignees."""
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/goalPlanAssignees?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_goal_plan_assignees_chunk, offset) for offset in offsets]):
            goal_plan_assignees_data.extend(future.result())

    return goal_plan_assignees_data

def generate_report3():
    """Generate and store goal plan assignees report."""
    try:
        goal_plan_assignees = fetch_goal_plan_assignees()
        mapped_data = [map_goal_plan_assignees_data(assignee) for assignee in goal_plan_assignees]

        if mapped_data:
            collection.insert_many(mapped_data)
            message = f"Inserted {len(mapped_data)} goal plan assignees records successfully."
        else:
            message = "No goal plan assignees records found."
        print(message)
        return message

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return f"Error fetching data: {e}"
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}"
