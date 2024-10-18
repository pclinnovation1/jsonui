from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# Oracle Cloud HCM REST API base URL and credentials
ORACLE_HCM_BASE_URL = 'https://iaihgs-dev1.fa.ocs.oraclecloud.com/hcmRestApi/resources/11.13.18.05'
USERNAME = 'Vishal.Meena@payrollcloudcorp.com'  # Replace with your actual username
PASSWORD = 'Welcome#12345'  # Replace with your actual password

# Function to get element entries using the person number
def get_element_entries_by_person_number(person_number):
    # API URL to fetch element entries using person number
    api_url = f"{ORACLE_HCM_BASE_URL}/elementEntries?q=PersonNumber='{person_number}'&limit=10&onlyData=true"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Make the GET request to Oracle Cloud API
    response = requests.get(api_url, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD))

    # Check the response status
    if response.status_code == 200:
        data = response.json()
        if data.get("items"):
            # Return the first element entry found
            return data["items"]
    return None

# Function to fetch detailed element entry information using elementEntriesUniqID
def get_element_entry_details(elementEntriesUniqID):
    api_url = f"{ORACLE_HCM_BASE_URL}/elementEntries/{elementEntriesUniqID}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Make the GET request to Oracle Cloud API
    response = requests.get(api_url, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD))

    # Check the response status
    if response.status_code == 200:
        return response.json()
    return {"error": f"Failed to fetch element entry details. Status code: {response.status_code}", "details": response.text}

# API endpoint to fetch element entry details using person number
@app.route('/api/element_entry', methods=['POST'])
def fetch_element_entry():
    # Get the JSON data from the request
    data = request.json
    person_number = data.get('person_number')

    if not person_number:
        return jsonify({"error": "person_number is required"}), 400

    # Step 1: Get element entry using person_number
    element_entry = get_element_entries_by_person_number(person_number)
    if not element_entry:
        return jsonify({"error": "No element entry found for the provided person_number"}), 404

    # Step 2: Extract the unique ID for the element entry
    # elementEntriesUniqID = element_entry.get("links", [])[0].get("href").split('/')[-1] if element_entry.get("links") else None
    # if not elementEntriesUniqID:
    #     return jsonify({"error": "Element entry ID not found"}), 404

    # # Step 3: Fetch detailed element entry information using the unique ID
    # detailed_entry = get_element_entry_details(elementEntriesUniqID)

    return jsonify(element_entry)

if __name__ == '__main__':
    app.run(debug=True)
