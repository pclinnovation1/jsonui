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
COLLECTION_NAME = CONFIG["mongodb"]["API_flowInstancesLOV"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Function to map flowInstancesLOV data
CONFIGURATION_MAPPING_FLOW_INSTANCES_LOV = {
    "status": "Status",
    "instance_name": "InstanceName",
    "errored": "Errored",
    "execution_mode": "ExecutionMode",
    "fi_completed_tasks": "FiCompletedTasks",
    "fi_process_date": "FiProcessDate",
    "fi_rolledback": "FiRolledback",
    "fi_task_flow_flag": "FiTaskFlowFlag",
    "fi_task_status": "FiTaskStatus",
    "fi_task_type": "FiTaskType",
    "fi_total_completed": "FiTotalCompleted",
    "instantiated_by": "InstantiatedBy",
    "marked_for_retry": "MarkedForRetry",
    "number_of_tasks": "NumberOfTasks",
    "progress": "Progress",
    "recur_time_component": "RecurTimeComponent",
    "recurring_flag": "RecurringFlag",
    "reversed": "Reversed",
    "schedule_end_date": "ScheduleEndDate",
    "scheduled_date": "ScheduledDate"
}

def map_flow_instances_lov_data(flow_instance_item):
    return {key: flow_instance_item.get(value, None) for key, value in CONFIGURATION_MAPPING_FLOW_INSTANCES_LOV.items()}

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
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/flowInstancesLOV?fields=FlowInstanceId,InstanceName&limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    # Use ThreadPoolExecutor to fetch worker data in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_workers_chunk, offset) for offset in offsets]):
            workers = future.result()
            for worker in workers:
                person_mapping[worker["FlowInstanceId"]] = worker["InstanceName"]

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
    idname["root_instance_name"] = mappings["RootFlowInstance"].get(flow_instance.get("RootFlowInstanceId"), "NA"),
    idname["legislative_data_group_name"] = mappings["LegislativeDataGroup"].get(flow_instance.get("LegislativeDataGroupId"), "NA"),
    idname["base_flow_name"] = mappings["BaseFlow"].get(flow_instance.get("BaseFlowId"), "NA"),
    idname["fi_payroll_name"] = mappings["Payroll"].get(flow_instance.get("FiPayrollId"), "NA")
    return idname

# Function to fetch flowInstancesLOV data
def fetch_flow_instances_lov():
    flow_instances_lov = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_flow_instances_lov_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/flowInstancesLOV?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_flow_instances_lov_chunk, offset) for offset in offsets]):
            flow_instances_lov.extend(future.result())

    return flow_instances_lov

def generate_report3():
    try:
        # Fetch flowInstancesLOV data
        flow_instances_lov_data = fetch_flow_instances_lov()

        mapped_data = []
        
        # Create mappings
        mappingsidname = {
            "RootFlowInstance": fetch_RootFlowInstanceId_to_RootFlowInstanceName_mapping(),
            "LegislativeDataGroup": fetch_LegislativeDataGroupId_to_Name_mapping(),
            "BaseFlow": fetch_BaseFlowId_to_BaseFlowName_mapping(),
            "Payroll": fetch_PayrollId_to_PayrollName_mapping()
        }
        # Map flowInstancesLOV data
        for flow_instance in flow_instances_lov_data:
            idname = update_Id_with_names(flow_instance, mappingsidname)
            mapped_flow_instance_data = map_flow_instances_lov_data(flow_instance)
            mapped_flow_instance_data.update(idname)
            mapped_data.append(mapped_flow_instance_data)

        # If mapped data is not empty, insert it into MongoDB
        if mapped_data:
            collection.insert_many(mapped_data)
            message = f"Inserted {len(mapped_data)} flow instances LOV records successfully."
        else:
            message = "No flow instances LOV records found."

        print(message)
        return jsonify({"message": message}), 200

    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching data: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
