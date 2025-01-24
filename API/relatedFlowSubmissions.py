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
COLLECTION_NAME = CONFIG["mongodb"]["API_relatedFlowSubmissions"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]


# Configuration mapping for Flow Submissions
CONFIGURATION_MAPPING_FLOW_SUBMISSIONS = {
    "base_flow_name": "BaseFlowName",
    "flow_name": "FlowName",
    "description": "Description",
    "legislation_code": "LegislationCode"
}

# Function to map Flow Submission data
def map_flow_submission_data(flow_submission_item):
    return {key: flow_submission_item.get(value, None) for key, value in CONFIGURATION_MAPPING_FLOW_SUBMISSIONS.items()}

# Function to fetch Person ID to Person Number mapping
def fetch_LegislativeDataGroupId_to_Name_mapping():
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    person_mapping = {}

    # Function to fetch a chunk of worker data
    def fetch_workers_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/legislativeDataGroupsLOV?fields=LegislativeDataGroupId,Name&limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    # Use ThreadPoolExecutor to fetch worker data in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_workers_chunk, offset) for offset in offsets]):
            workers = future.result()
            for worker in workers:
                person_mapping[worker["LegislativeDataGroupId"]] = worker["Name"]

    return person_mapping

# Update assignment data with names
def update_Id_with_names(flow_submission, mappings):
    """
    Replace IDs in assignment data with corresponding names using the mappings.
    """
    idname={}
    idname["legislative_data_group_name"] = mappings["LegislativeDataGroup"].get(flow_submission.get("LegislativeDataGroupId"), "NA")
    return idname

# Function to fetch Flow Submissions data
def fetch_flow_submissions():
    flow_submissions = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_flow_submissions_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/relatedFlowSubmissions?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_flow_submissions_chunk, offset) for offset in offsets]):
            flow_submissions.extend(future.result())

    return flow_submissions

def generate_report3():
    """Route to fetch and return related flow submissions data."""
    try:
        # Fetch flow submissions data
        flow_submissions_data = fetch_flow_submissions()

        mapped_data = []
        # Create mappings
        mappingsidname = {
            "LegislativeDataGroup": fetch_LegislativeDataGroupId_to_Name_mapping()
        }
        # Map flow submissions data
        for flow_submission in flow_submissions_data:
            idname = update_Id_with_names(flow_submission, mappingsidname)
            mapped_flow_submission_data=map_flow_submission_data(flow_submission)
            mapped_flow_submission_data.update(idname)
            mapped_data.append(mapped_flow_submission_data)

        # If mapped data is not empty, insert it into MongoDB
        if mapped_data:
            collection.insert_many(mapped_data)
            message = f"Inserted {len(mapped_data)} flow submission records successfully."
        else:
            message = "No flow submission records found."

        print(message)
        return message

    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching data: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
