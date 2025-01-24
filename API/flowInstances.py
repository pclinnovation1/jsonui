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
COLLECTION_NAME = CONFIG["mongodb"]["API_flowInstances"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Configuration mapping for Flow Instances
CONFIGURATION_MAPPING_FLOW_INSTANCES = {
    "flow_name": "FlowName",
    "group_status": "GroupStatus",
    "is_extract": "IsExtract",
    "is_data_loader": "IsDataLoader",
    "task_type": "TaskType",
    "number_of_tasks": "NumberOfTasks",
    "completed_tasks": "CompletedTasks",
    "created_by": "CreatedBy",
    "creation_date": "CreationDate",
    "scheduled_date": "ScheduledDate",
    "schedule_end_date": "ScheduleEndDate",
    "recurring_flag": "RecurringFlag",
    "records": "Records",
    "process_date": "ProcessDate",
    "last_updated_by": "LastUpdatedBy",
    "last_update_date": "LastUpdateDate",
    "status": "Status"
}

# Function to map Flow Instances data
def map_flow_instances_data(flow_instance_item):
    return {key: flow_instance_item.get(value, None) for key, value in CONFIGURATION_MAPPING_FLOW_INSTANCES.items()}

# Function to fetch Person ID to Person Number mapping
def fetch_RootFlowInstanceId_to_RootFlowInstanceName_mapping():
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    person_mapping = {}

    # Function to fetch a chunk of worker data
    def fetch_workers_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/flowInstances?fields=FlowInstanceId,FlowName&limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    # Use ThreadPoolExecutor to fetch worker data in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_workers_chunk, offset) for offset in offsets]):
            workers = future.result()
            for worker in workers:
                person_mapping[worker["FlowInstanceId"]] = worker["FlowName"]

    return person_mapping

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

# Function to fetch Person ID to Person Number mapping
def fetch_BaseFlowId_to_BaseFlowName_mapping():
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    person_mapping = {}

    # Function to fetch a chunk of worker data
    def fetch_workers_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/flowPatterns?fields=BaseFlowId,BaseFlowName&limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    # Use ThreadPoolExecutor to fetch worker data in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_workers_chunk, offset) for offset in offsets]):
            workers = future.result()
            for worker in workers:
                person_mapping[worker["BaseFlowId"]] = worker["BaseFlowName"]

    return person_mapping

# Function to fetch Person ID to Person Number mapping
def fetch_PayrollId_to_PayrollName_mapping():
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    person_mapping = {}

    # Function to fetch a chunk of worker data
    def fetch_workers_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/payrollDefinitionsLOV?fields=PayrollId,PayrollName&limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    # Use ThreadPoolExecutor to fetch worker data in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_workers_chunk, offset) for offset in offsets]):
            workers = future.result()
            for worker in workers:
                person_mapping[worker["PayrollId"]] = worker["PayrollName"]

    return person_mapping

# Update assignment data with names
def update_Id_with_names(flow_instance, mappings):
    """
    Replace IDs in assignment data with corresponding names using the mappings.
    """
    idname={}
    idname["root_flow_name"] = mappings["RootFlowInstance"].get(flow_instance.get("RootFlowInstanceId"), "NA"),
    idname["legislative_data_group_name"] = mappings["LegislativeDataGroup"].get(flow_instance.get("LegislativeDataGroupId"), "NA"),
    idname["base_flow_name"] = mappings["BaseFlow"].get(flow_instance.get("BaseFlowId"), "NA"),
    idname["payroll_name"] = mappings["Payroll"].get(flow_instance.get("PayrollId"), "NA")
    return idname

# Function to fetch Flow Instances data
def fetch_flow_instances():
    flow_instances = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_flow_instances_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/flowInstances?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_flow_instances_chunk, offset) for offset in offsets]):
            flow_instances.extend(future.result())

    return flow_instances

def generate_report3():
    """Route to fetch and return flow instances data."""
    try:
        # Fetch flow instances data
        flow_instances_data = fetch_flow_instances()

        mapped_data = []
        
        # Create mappings
        mappingsidname = {
            "RootFlowInstance": fetch_RootFlowInstanceId_to_RootFlowInstanceName_mapping(),
            "LegislativeDataGroup": fetch_LegislativeDataGroupId_to_Name_mapping(),
            "BaseFlow": fetch_BaseFlowId_to_BaseFlowName_mapping(),
            "Payroll": fetch_PayrollId_to_PayrollName_mapping()
        }
        # Map flow instances data
        for flow_instance in flow_instances_data:
            idname = update_Id_with_names(flow_instance, mappingsidname)
            mapped_flow_instance_data=map_flow_instances_data(flow_instance)
            mapped_flow_instance_data.update(idname)
            mapped_data.append(mapped_flow_instance_data)

        # If mapped data is not empty, insert it into MongoDB
        if mapped_data:
            collection.insert_many(mapped_data)
            message = f"Inserted {len(mapped_data)} flow instances records successfully."
        else:
            message = "No flow instances records found."

        print(message)
        return message

    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching data: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
