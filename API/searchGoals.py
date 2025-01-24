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
COLLECTION_NAME = CONFIG["mongodb"]["API_searchGoals"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]


# Configuration mapping for Search Goals
CONFIGURATION_MAPPING_SEARCH_GOALS = {
    "goal_name": "GoalName",
    "Person_name": "WorkerName",
    "person_number": "PersonNumber",
    "worker_assignment_name": "WorkerAssignmentName",
    "worker_assignment_number": "WorkerAssignmentNumber",
    "description": "Description",
    "start_date": "StartDate",
    "target_completion_date": "TargetCompletionDate",
    "actual_completion_date": "ActualCompletionDate",
    "job_name": "JobName",
    "manager_name": "ManagerName",
    "status_code": "StatusCode",
    "department": "DepartmentName",
    "business_unit": "BusinessUnitName",
    "location_name": "Location",
    "goal_type_code": "GoalTypeCode",
    "perf_goal_type": "PerfGoalType",
    "manager_type": "ManagerType",
    "status_code_meaning": "StatusCodeMeaning"
}

# Function to map Search Goals data
def map_search_goals_data(goal_item):
    return {key: goal_item.get(value, None) for key, value in CONFIGURATION_MAPPING_SEARCH_GOALS.items()}

# Function to fetch Search Goals data
def fetch_search_goals():
    search_goals = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_search_goals_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/searchGoals?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_search_goals_chunk, offset) for offset in offsets]):
            search_goals.extend(future.result())

    return search_goals

# Function to fetch Person ID to Person Number mapping
def fetch_ReviewPeriodId_to_ReviewPeriodName_mapping():
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    person_mapping = {}

    # Function to fetch a chunk of worker data
    def fetch_workers_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/reviewPeriodsLOV?fields=ReviewPeriodId,ReviewPeriodName&limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    # Use ThreadPoolExecutor to fetch worker data in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_workers_chunk, offset) for offset in offsets]):
            workers = future.result()
            for worker in workers:
                person_mapping[worker["ReviewPeriodId"]] = worker["ReviewPeriodName"]

    return person_mapping

# Function to fetch Person ID to Person Number mapping
def fetch_GoalPlanId_to_GoalPlanName_mapping():
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    person_mapping = {}

    # Function to fetch a chunk of worker data
    def fetch_workers_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/goalPlansLOV?fields=GoalPlanId,GoalPlanName&limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    # Use ThreadPoolExecutor to fetch worker data in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_workers_chunk, offset) for offset in offsets]):
            workers = future.result()
            for worker in workers:
                person_mapping[worker["GoalPlanId"]] = worker["GoalPlanName"]

    return person_mapping

# Update assignment data with names
def update_goal_with_names(goal, mappings):
    """
    Replace IDs in assignment data with corresponding names using the mappings.
    """
    idname={}
    idname["review_period_name"] = mappings["ReviewPeriod"].get(goal.get("ReviewPeriodId"), "NA")
    idname["goal_plan_name"] = mappings["GoalPlan"].get(goal.get("GoalPlanId"), "NA")
    return idname


def generate_report3():
    """Route to fetch and return search goals data."""
    try:
        # Fetch search goals data
        search_goals_data = fetch_search_goals()

        mapped_data = []
        # Create mappings
        mappingsidname = {
            "ReviewPeriod": fetch_ReviewPeriodId_to_ReviewPeriodName_mapping(),
            "GoalPlan": fetch_GoalPlanId_to_GoalPlanName_mapping()
        }
        
        # Map search goals data
        for goal in search_goals_data:
            idname = update_goal_with_names(goal, mappingsidname)
            mapped_goal_data=map_search_goals_data(goal)
            # Merge idname into the mapped_goal_data
            mapped_goal_data.update(idname)  # Merge idname dictionary with mapped goal data
            mapped_data.append(mapped_goal_data)

        # If mapped data is not empty, insert it into MongoDB
        if mapped_data:
            collection.insert_many(mapped_data)
            message = f"Inserted {len(mapped_data)} search goal records successfully."
        else:
            message = "No search goal records found."

        print(message)
        return message

    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching data: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
