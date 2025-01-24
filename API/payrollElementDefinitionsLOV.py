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
COLLECTION_NAME = CONFIG["mongodb"]["API_payrollElementDefinitionsLOV"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Function to map payrollElementDefinitionsLOV data
CONFIGURATION_MAPPING_PAYROLL_ELEMENT_DEFINITIONS = {
    "effective_start_date": "EffectiveStartDate",
    "effective_end_date": "EffectiveEndDate",
    "element_name": "ElementName",
    "reporting_name": "ReportingName",
    "use_at_relationship_level": "UseAtRelationshipLevel",
    "use_at_assignment_level": "UseAtAssignmentLevel",
    "processing_type": "ProcessingType",
    "legislation_code": "LegislationCode",
    "input_currency_code": "InputCurrencyCode",
    "output_currency_code": "OutputCurrencyCode",
    "primary_classification_name": "PrimaryClassificationName",
    "legislative_data_group_name": "LegislativeDataGroupName",
    "secondary_classification_name": "SecondaryClassificationName",
    "category_code": "CategoryCode"
}

def map_payroll_element_definitions_data(element_definition_item):
    return {key: element_definition_item.get(value, None) for key, value in CONFIGURATION_MAPPING_PAYROLL_ELEMENT_DEFINITIONS.items()}

# Function to fetch Person ID to Person Number mapping
def fetch_person_id_to_number_mapping():
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    person_mapping = {}

    # Function to fetch a chunk of worker data
    def fetch_workers_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/workers?fields=PersonId,PersonNumber&limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    # Use ThreadPoolExecutor to fetch worker data in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_workers_chunk, offset) for offset in offsets]):
            workers = future.result()
            for worker in workers:
                person_mapping[worker["PersonId"]] = worker["PersonNumber"]

    return person_mapping

def update_Id_with_names(flow_instance, mappings):
    """
    Replace IDs in assignment data with corresponding names using the mappings.
    """
    idname={}
    idname["person_number"] = mappings["person_mapping"].get(flow_instance.get("PersonId"), "NA")
    return idname

# Function to fetch payrollElementDefinitionsLOV data
def fetch_payroll_element_definitions():
    payroll_element_definitions = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_payroll_element_definitions_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/payrollElementDefinitionsLOV?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_payroll_element_definitions_chunk, offset) for offset in offsets]):
            payroll_element_definitions.extend(future.result())

    return payroll_element_definitions

def generate_report3():
    try:
        # Fetch payrollElementDefinitionsLOV data
        payroll_element_definitions_data = fetch_payroll_element_definitions()

        mapped_data = []
        
        # Create mappings
        mappingsidname = {
            "person_mapping":fetch_person_id_to_number_mapping()
        }
        
        # Map payrollElementDefinitionsLOV data
        for element_definition in payroll_element_definitions_data:
            idname = update_Id_with_names(element_definition, mappingsidname)
            mapped_element_definition_data = map_payroll_element_definitions_data(element_definition)
            mapped_element_definition_data.update(idname)
            mapped_data.append(mapped_element_definition_data)

        # If mapped data is not empty, insert it into MongoDB
        if mapped_data:
            collection.insert_many(mapped_data)
            message = f"Inserted {len(mapped_data)} payroll element definitions records successfully."
        else:
            message = "No payroll element definitions records found."

        print(message)
        return message

    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching data: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
