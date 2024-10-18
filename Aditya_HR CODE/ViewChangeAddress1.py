from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# Oracle Cloud API base URL
BASE_URL = "https://iaihgs-dev1.fa.ocs.oraclecloud.com:443"

# Hardcoded username and password for Basic Authentication
USERNAME = "Vishal.Meena@payrollcloudcorp.com"  # Replace with your actual username
PASSWORD = "Welcome#12345"  # Replace with your actual password

# API 1: Fetch employee data and automatically call API 2 for address update
@app.route('/update_employee_address', methods=['POST'])
def update_employee_address():
    try:
        # Get the input JSON (must include personNumber and address details)
        data = request.json
        if not data or "personNumber" not in data:
            return jsonify({"error": "personNumber and address details are required"}), 400

        personNumber = data['personNumber']
        address_data = {
            "AddressLine1": data.get("AddressLine1"),
            "AddressLine2": data.get("AddressLine2"),
            "AddressLine3": data.get("AddressLine3"),
            "City": data.get("City"),
            "Region": data.get("Region"),
            "Region2": data.get("Region2"),
            "Country": data.get("Country"),
            "PostalCode": data.get("PostalCode")
            # "EffectiveStartDate": data.get("EffectiveStartDate")
        }

        # Step 1: Fetch employee details using personNumber (API 1)
        api1_url = f"{BASE_URL}/hcmRestApi/resources/11.13.18.05/emps?q=PersonNumber={personNumber}&expand=all&limit=1"
        
        headers = {
            "Content-Type": "application/json"
        }

        # Send GET request to fetch employee data based on personNumber
        response = requests.get(api1_url, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD))

        # Handle API 1 response
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                # Extract the unique employee ID from the "parent" link
                parent_href = data['items'][0]['links'][2]['href']
                empsUniqID = parent_href.split("/lov")[0].split("/emps/")[1]
                print(empsUniqID)

                # Step 2: Update employee address using API 2 with the fetched empsUniqID
                api2_url = f"{BASE_URL}/hcmRestApi/resources/11.13.18.05/emps/{empsUniqID}"

                # Send PATCH request to update employee address
                response = requests.patch(api2_url, json=address_data, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD))

                # Handle API 2 response
                if response.status_code == 200:
                    return jsonify({"message": "Employee address updated successfully", "data": response.json()}), 200
                else:
                    return jsonify({"error": "Failed to update employee address", "details": response.text}), response.status_code
            else:
                return jsonify({"error": "No employee data found for the provided personNumber"}), 404
        else:
            return jsonify({"error": "Failed to fetch employee data", "details": response.text}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# New Route: View Employee Address using personNumber (POST Method)
@app.route('/view_employee_address', methods=['POST'])
def view_employee_address():
    try:
        # Get the input JSON (must include personNumber)
        data = request.json
        personNumber = data.get('personNumber')
        if not personNumber:
            return jsonify({"error": "personNumber is required"}), 400

        # Step 1: Fetch employee details using personNumber (API 1)
        api1_url = f"{BASE_URL}/hcmRestApi/resources/11.13.18.05/emps?q=PersonNumber={personNumber}&expand=all&limit=1"
        
        headers = {
            "Content-Type": "application/json"
        }

        # Send GET request to fetch employee data based on personNumber
        response = requests.get(api1_url, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD))

        # Handle API 1 response
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                # Extract and return the address details
                employee_data = data['items'][0]
                address_info = {
                    "AddressLine1": employee_data.get("AddressLine1"),
                    "AddressLine2": employee_data.get("AddressLine2"),
                    "AddressLine3": employee_data.get("AddressLine3"),
                    "City": employee_data.get("City"),
                    "Region": employee_data.get("Region"),
                    "Region2": employee_data.get("Region2"),
                    "Country": employee_data.get("Country"),
                    "PostalCode": employee_data.get("PostalCode")
                }
                return jsonify({"employeeAddress": address_info}), 200
            else:
                return jsonify({"error": "No employee data found for the provided personNumber"}), 404
        else:
            return jsonify({"error": "Failed to fetch employee data", "details": response.text}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
