

import pytesseract
from PIL import Image
import openai
import json
import pandas as pd
from jinja2 import Template
from fuzzywuzzy import process
import numpy as np

# Set your OpenAI API key
# openai.api_key = ''  # Replace with your OpenAI API key

# Path to the invoice image file
image_path = 'alpha.jpg'  # Path to the uploaded image file
excel_path_nominal_account = 'Data.xlsx'

# Open the image file
img = Image.open(image_path)

# Use Tesseract to do OCR on the image
extracted_text = pytesseract.image_to_string(img)

print("Extracted Text from Image:")
print(extracted_text)

# Read the prompt details from the JSON file
with open('prompt_details.json', 'r') as file:
    prompt_details = json.load(file)

# Read the enhanced prompt template from the text file
with open('enhanced_invoice_prompt.txt', 'r') as file:
    prompt_template = file.read()

# Create a Jinja2 template from the prompt file
template = Template(prompt_template)

# Function to join multiple terms for each field
def join_terms(terms):
    return ', '.join(terms)

# Construct the dictionary to safely format the prompt
prompt_values = {
    "property_reference": join_terms(prompt_details['property_reference']),
    "supplier_name": join_terms(prompt_details['supplier_name']),
    "demand_date": join_terms(prompt_details['demand_date']),
    "amount_due": join_terms(prompt_details['amount_due']),
    "balance_brought_forward": join_terms(prompt_details['balance_brought_forward']),
    "account_balance": join_terms(prompt_details['account_balance']),
    "due_date": join_terms(prompt_details['due_date']),
    "business_unit": join_terms(prompt_details['business_unit']),
    "unique_code": join_terms(prompt_details['unique_code']),
    "sender_address": join_terms(prompt_details['sender_address']),
    "receiver_address": join_terms(prompt_details['receiver_address']),
    "invoice_type": join_terms(prompt_details['invoice_type']),
    "extracted_text": extracted_text
}

# Render the prompt using Jinja2
prompt = template.render(prompt_values)

# Call the OpenAI model with the completion endpoint
response = openai.Completion.create(
    model="gpt-3.5-turbo-instruct",
    prompt=prompt,
    max_tokens=1000,
    temperature=0.7
)

structured_data = response.choices[0].text.strip()

print("Structured Data from GPT-3.5:")
print(structured_data)

# Properly handle multiple JSON objects
try:
    structured_data_list = structured_data.split('\n\n')
    structured_data_list = [json.loads(data) for data in structured_data_list]
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
    structured_data_list = []

# Example mapping JSON (JSON 2)
mapping_json = {
    "property_reference": ["Property Reference", "Reference Number", "Property ID", "Property Ref"],
    "supplier_name": ["Supplier Name", "Vendor Name", "Service Provider", "Supplier", "Vendor"],
    "demand_date": ["Demand Date", "Date of Demand", "Invoice Date", "Billing Date"],
    "amount_due": ["Amount Due", "Total Due", "Due Amount", "Outstanding Amount", "Balance Due"],
    "balance_brought_forward": ["Balance Brought Forward", "Previous Balance", "Carried Forward Balance", "Outstanding Balance"],
    "account_balance": ["Account Balance", "Current Balance", "Balance"],
    "due_date": ["Due Date", "Payment Due Date", "Deadline", "Payment Deadline"],
    "business_unit": ["Business Unit", "Department", "Division", "Unit"],
    "unique_code": ["Unique Code", "Reference Code", "ID Code", "Code"],
    "sender_address": ["Sender's Address", "From Address", "Origin Address", "Return Address"],
    "receiver_address": ["Receiver's Address", "Receiver's Reference", "Mailing Address", "Shipping Address", "Delivery Address", "Destination Address", "Postal Address"],
    "invoice_type": ["Invoice Type", "Type of Invoice", "Billing Type", "Invoice Category"]
}

# Function to normalize strings
def normalize_string(s):
    return ''.join(e for e in s if e.isalnum()).lower()

# Function to map fields from JSON 1 to JSON 3 using JSON 2 and get Account_Number
def map_fields_get_account_number(structured_data, mapping_json, account_mapping):
    structured_data_dict = structured_data
    mapped_data = {}

    for key, values in mapping_json.items():
        if key in structured_data_dict:
            for field in values:
                mapped_data[field] = structured_data_dict[key]

    # Normalize account mapping
    account_mapping['Normalized_Account_ID'] = account_mapping['Account_ID'].apply(normalize_string)

    # Normalize invoice_type
    invoice_type = structured_data_dict.get('invoice_type', None)
    if invoice_type:
        normalized_invoice_type = normalize_string(invoice_type)
        # Use fuzzy matching to find the best match
        best_match = process.extractOne(normalized_invoice_type, account_mapping['Normalized_Account_ID'], score_cutoff=40)
        if best_match:
            account_number = int(account_mapping.loc[account_mapping['Normalized_Account_ID'] == best_match[0], 'Account_Number'].values[0])
            mapped_data['Account_Number'] = account_number
            print_matched_values('Invoice Type', invoice_type, best_match[0], account_number)

    return mapped_data

# Function to map fields from JSON 1 to JSON 3 using JSON 2 and get Cost_Centre
def map_fields_get_cost_centre(structured_data, mapping_json, business_area_mapping):
    structured_data_dict = structured_data
    mapped_data = {}

    for key, values in mapping_json.items():
        if key in structured_data_dict:
            for field in values:
                mapped_data[field] = structured_data_dict[key]

    # Normalize business area mapping
    business_area_mapping['Normalized_Address'] = business_area_mapping['Address'].apply(normalize_string)

    # Normalize receiver_address
    receiver_address = structured_data_dict.get('receiver_address', None)
    if receiver_address:
        normalized_receiver_address = normalize_string(receiver_address)
        # Use fuzzy matching to find the best match
        best_match = process.extractOne(normalized_receiver_address, business_area_mapping['Normalized_Address'], score_cutoff=40)
        if best_match:
            cost_centre = int(business_area_mapping.loc[business_area_mapping['Normalized_Address'] == best_match[0], 'Cost_Centre'].values[0])
            mapped_data['Cost_Centre'] = cost_centre
            print_matched_values('Receiver Address', receiver_address, best_match[0], cost_centre)

    return mapped_data

# Function to map fields from JSON 1 to JSON 3 using JSON 2 and get Legal_Entity
def map_fields_get_legal_entity(structured_data, mapping_json, legal_entity_mapping):
    structured_data_dict = structured_data
    mapped_data = {}

    print("Legal Entity Mapping Columns:")
    print(legal_entity_mapping.columns)

    for key, values in mapping_json.items():
        if key in structured_data_dict:
            for field in values:
                mapped_data[field] = structured_data_dict[key]

    # Normalize legal entity mapping
    legal_entity_mapping['Normalized_Legal_Entity'] = legal_entity_mapping['Legal_Entity'].apply(normalize_string)

    # Normalize sender_address
    sender_address = structured_data_dict.get('sender_address', None)
    if sender_address:
        normalized_sender_address = normalize_string(sender_address)
        # Use fuzzy matching to find the best match
        best_match = process.extractOne(normalized_sender_address, legal_entity_mapping['Normalized_Legal_Entity'], score_cutoff=40)
        if best_match:
            legal_entity = legal_entity_mapping.loc[legal_entity_mapping['Normalized_Legal_Entity'] == best_match[0], 'Entity_Code'].values[0]
            mapped_data['Legal_Entity'] = legal_entity
            print_matched_values('Sender Address', sender_address, best_match[0], legal_entity)

    return mapped_data

# Function to print matched values
def print_matched_values(label, from_value, matched_value, code_value):
    print(f"{label} from Invoice: {from_value}")
    print(f"Best Match from Excel: {matched_value}")
    print(f"Code Value: {code_value}")

# Read the Excel files
account_mapping = pd.read_excel(excel_path_nominal_account, sheet_name='1_Nominal_Account')
business_area_mapping = pd.read_excel(excel_path_nominal_account, sheet_name='2_Business_Area')
legal_entity_mapping = pd.read_excel(excel_path_nominal_account, sheet_name='3_Legal_Entity')

# Check columns in legal_entity_mapping
print("Columns in 3_Legal_Entity sheet:")
print(legal_entity_mapping.columns)

# Function to convert values to JSON serializable types
def convert_to_serializable(data):
    for key, value in data.items():
        if isinstance(value, pd._libs.tslibs.timestamps.Timestamp):
            data[key] = value.strftime('%Y-%m-%d')
        elif isinstance(value, (pd.Series, pd.DataFrame)):
            data[key] = value.to_json()
        elif isinstance(value, np.int64):
            data[key] = int(value)
    return data

# Map the fields for each structured JSON object and get Account_Number, Cost_Centre, and Legal_Entity
mapped_structured_data_list = []
for data in structured_data_list:
    mapped_data = map_fields_get_account_number(data, mapping_json, account_mapping)
    mapped_data = {**mapped_data, **map_fields_get_cost_centre(data, mapping_json, business_area_mapping)}
    mapped_data = {**mapped_data, **map_fields_get_legal_entity(data, mapping_json, legal_entity_mapping)}
    mapped_data = convert_to_serializable(mapped_data)  # Convert to JSON serializable types
    mapped_structured_data_list.append(mapped_data)

# Print the final mapped structured data and account number
for idx, data in enumerate(mapped_structured_data_list):
    print(f"Mapped Structured Data {idx+1}:")
    print(json.dumps(data, indent=4))




alpha = ''
# Print Account Numbers, Cost Centres, and Legal Entities at the end
print("\nAccount Numbers, Cost Centres, and Legal Entities:")
for data in mapped_structured_data_list:
    if 'Account_Number' in data:
        print(f"Account_Number: {data['Account_Number']}")
        alpha += str(data["Account_Number"]) + "-"
    else: 
        alpha += "00000-"
    if 'Cost_Centre' in data:
        print(f"Cost_Centre: {data['Cost_Centre']}")
        alpha += str(data["Cost_Centre"]) + "-"
    else: 
        alpha += "00000-"
    if 'Legal_Entity' in data:
        print(f"Legal_Entity: {data['Legal_Entity']}")
        alpha += str(data["Legal_Entity"])
    else: 
        alpha += "00000"
    

print("Generated code is below:  ", alpha)



