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
COLLECTION_NAME = CONFIG["mongodb"]["API_organizationPaymentMethodsLOV"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Function to map organizationPaymentMethodsLOV data
CONFIGURATION_MAPPING_ORG_PAYMENT_METHODS = {
    "base_org_payment_method_name": "BaseOrgPayMethodName",
    "org_payment_method_name": "OrgPaymentMethodName",
    "currency_code": "CurrencyCode",
    "effective_end_date": "EffectiveEndDate",
    "effective_start_date": "EffectiveStartDate",
    "payment_type_name": "PaymentTypeName",
    "category": "Category",
    "legislation_code": "LegislationCode"
}

def map_org_payment_methods_data(payment_method_item):
    return {key: payment_method_item.get(value, None) for key, value in CONFIGURATION_MAPPING_ORG_PAYMENT_METHODS.items()}

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

def update_Id_with_names(flow_instance, mappings):
    """
    Replace IDs in assignment data with corresponding names using the mappings.
    """
    idname={}
    idname["legislative_data_group_name"] = mappings["LegislativeDataGroup"].get(flow_instance.get("LegislativeDataGroupId"), "NA")
    return idname

# Function to fetch organizationPaymentMethodsLOV data
def fetch_org_payment_methods():
    org_payment_methods = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_org_payment_methods_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/organizationPaymentMethodsLOV?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_org_payment_methods_chunk, offset) for offset in offsets]):
            org_payment_methods.extend(future.result())

    return org_payment_methods

def generate_report3():
    try:
        # Fetch organizationPaymentMethodsLOV data
        org_payment_methods_data = fetch_org_payment_methods()

        mapped_data = []
        
        # Create mappings
        mappingsidname = {
            "LegislativeDataGroup": fetch_LegislativeDataGroupId_to_Name_mapping()
        }
        
        # Map organizationPaymentMethodsLOV data
        for payment_method in org_payment_methods_data:
            idname = update_Id_with_names(payment_method, mappingsidname)
            mapped_payment_method_data = map_org_payment_methods_data(payment_method)
            mapped_payment_method_data.update(idname)
            mapped_data.append(mapped_payment_method_data)

        # If mapped data is not empty, insert it into MongoDB
        if mapped_data:
            collection.insert_many(mapped_data)
            message = f"Inserted {len(mapped_data)} organization payment methods records successfully."
        else:
            message = "No organization payment methods records found."

        print(message)
        return message

    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching data: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
