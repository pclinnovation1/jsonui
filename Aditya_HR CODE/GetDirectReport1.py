# from flask import Flask, request, jsonify
# import requests
# from requests.auth import HTTPBasicAuth

# # Initialize Flask app
# app = Flask(__name__)

# # Oracle API credentials (update with your actual credentials)
# oracle_username = 'Vishal.Meena@payrollcloudcorp.com'
# oracle_password = 'Welcome#12345'

# # Function to get all direct reports of an employee
# def get_direct_reports(emps_uniq_id, query_params, person_number):
#     # API URL for fetching direct reports
#     oracle_api_url = f'https://iaihgs-dev1.fa.ocs.oraclecloud.com/hcmRestApi/resources/11.13.18.05/emps/{emps_uniq_id}/child/directReports'

#     # Headers
#     headers = {
#         'Content-Type': 'application/json',
#         'Accept': 'application/json'
#     }

#     # Make the GET request to fetch direct reports
#     response = requests.get(oracle_api_url, headers=headers, auth=HTTPBasicAuth(oracle_username, oracle_password), params=query_params)

#     # Check the response status and content
#     if response.status_code == 200:
#         result = response.json()
#         # Modify the result to include person_number instead of person_id
#         for item in result['items']:
#             item['PersonNumber'] = person_number  # Add the person number from input
#             del item['PersonId']  # Remove the PersonId if needed
#         return result, 200  # Return the modified list of direct reports
#     elif response.status_code == 404:
#         return {"error": "Employee ID not found or no direct reports available.", "details": response.text}, 404
#     else:
#         return {"error": f"Failed to fetch direct reports. Status code: {response.status_code}", "details": response.text}, response.status_code

# # API endpoint to fetch direct reports of an employee using POST
# @app.route('/api/direct-reports', methods=['POST'])
# def fetch_direct_reports():
#     # Get the JSON data from the request
#     data = request.json

#     # Get person_number from the JSON body
#     person_number = data.get('person_number')
#     if not person_number:
#         return jsonify({"error": "Person number is required"}), 400

#     # Collect optional query parameters from the request JSON body
#     query_params = {
#         'dependency': data.get('dependency'),
#         'expand': data.get('expand'),
#         'fields': data.get('fields'),
#         'finder': data.get('finder'),
#         'limit': data.get('limit'),
#         'links': data.get('links'),
#         'offset': data.get('offset'),
#         'onlyData': data.get('onlyData'),
#         'orderBy': data.get('orderBy'),
#         'q': data.get('q'),
#         'totalResults': data.get('totalResults')
#     }

#     # Remove any keys with None values
#     query_params = {k: v for k, v in query_params.items() if v is not None}

#     # Assume you already know the employee's unique ID (emps_uniq_id) based on person_number
#     # In a real scenario, you may need to fetch it using another API call
#     emps_uniq_id = get_employee_unique_id(person_number)
#     if not emps_uniq_id:
#         return jsonify({"error": "Employee not found"}), 404

#     # Call the function to get direct reports, passing person_number as well
#     result, status_code = get_direct_reports(emps_uniq_id, query_params, person_number)

#     # Return the result as JSON
#     return jsonify(result), status_code

# # Function to get the employee unique ID based on the person number (assumed implementation)
# def get_employee_unique_id(person_number):
#     # Make a request to fetch employee details using person number
#     url = f'https://iaihgs-dev1.fa.ocs.oraclecloud.com/hcmRestApi/resources/11.13.18.05/emps?q=PersonNumber=\'{person_number}\''
#     response = requests.get(url, auth=HTTPBasicAuth(oracle_username, oracle_password))

#     if response.status_code == 200:
#         data = response.json()
#         if data["items"]:
#             # Return the unique ID of the first matching employee
#             return data["items"][0]["links"][0]["href"].split('/')[-1]
#     return None

# # Run the Flask app
# if __name__ == '__main__':
#     app.run(debug=True)
























from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth

# Initialize Flask app
app = Flask(__name__)

# Oracle API credentials (update with your actual credentials)
oracle_username = 'Vishal.Meena@payrollcloudcorp.com'
oracle_password = 'Welcome#12345'

# Function to get all direct reports of an employee
def get_direct_reports(emps_uniq_id, query_params):
    # API URL for fetching direct reports
    oracle_api_url = f'https://iaihgs-dev1.fa.ocs.oraclecloud.com/hcmRestApi/resources/11.13.18.05/emps/{emps_uniq_id}/child/directReports'

    # Headers
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Make the GET request to fetch direct reports
    response = requests.get(oracle_api_url, headers=headers, auth=HTTPBasicAuth(oracle_username, oracle_password), params=query_params)

    # Check the response status and content
    if response.status_code == 200:
        direct_reports = response.json().get("items", [])

        # Modify each direct report to replace PersonId with PersonNumber
        for report in direct_reports:
            person_id = report.get("PersonId")
            if person_id:
                person_number = get_person_number_by_person_id(person_id)
                if person_number:
                    report["PersonNumber"] = person_number  # Add PersonNumber
                    del report["PersonId"]  # Remove PersonId

        return {"items": direct_reports}, 200  # Return the modified list of direct reports
    elif response.status_code == 404:
        return {"error": "Employee ID not found or no direct reports available.", "details": response.text}, 404
    else:
        return {"error": f"Failed to fetch direct reports. Status code: {response.status_code}", "details": response.text}, response.status_code

# Function to fetch the PersonNumber based on PersonId using API 2
def get_person_number_by_person_id(person_id):
    # API URL to fetch person number using PersonId
    url = f'https://iaihgs-dev1.fa.ocs.oraclecloud.com:443/hcmRestApi/resources/11.13.18.05/workers?expand=all&limit=1&q=PersonId={person_id}'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers, auth=HTTPBasicAuth(oracle_username, oracle_password))

    if response.status_code == 200:
        worker_data = response.json()
        if worker_data.get("items"):
            return worker_data["items"][0].get("PersonNumber")  # Get the PersonNumber
    return None

# API endpoint to fetch direct reports of an employee using POST
@app.route('/api/direct-reports', methods=['POST'])
def fetch_direct_reports():
    # Get the JSON data from the request
    data = request.json

    # Get person_number from the JSON body
    person_number = data.get('person_number')
    if not person_number:
        return jsonify({"error": "Person number is required"}), 400

    # Collect optional query parameters from the request JSON body
    query_params = {
        'dependency': data.get('dependency'),
        'expand': data.get('expand'),
        'fields': data.get('fields'),
        'finder': data.get('finder'),
        'limit': data.get('limit'),
        'links': data.get('links'),
        'offset': data.get('offset'),
        'onlyData': data.get('onlyData'),
        'orderBy': data.get('orderBy'),
        'q': data.get('q'),
        'totalResults': data.get('totalResults')
    }

    # Remove any keys with None values
    query_params = {k: v for k, v in query_params.items() if v is not None}

    # Fetch the employee's unique ID (emps_uniq_id) based on person_number
    emps_uniq_id = get_employee_unique_id(person_number)
    if not emps_uniq_id:
        return jsonify({"error": "Employee not found"}), 404

    # Call the function to get direct reports
    result, status_code = get_direct_reports(emps_uniq_id, query_params)

    # Return the result as JSON
    return jsonify(result), status_code

# Function to get the employee unique ID based on the person number (assumed implementation)
def get_employee_unique_id(person_number):
    # Make a request to fetch employee details using person number
    url = f'https://iaihgs-dev1.fa.ocs.oraclecloud.com/hcmRestApi/resources/11.13.18.05/emps?q=PersonNumber=\'{person_number}\''
    response = requests.get(url, auth=HTTPBasicAuth(oracle_username, oracle_password))

    if response.status_code == 200:
        data = response.json()
        if data["items"]:
            # Return the unique ID of the first matching employee
            return data["items"][0]["links"][0]["href"].split('/')[-1]
    return None

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
