from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# MongoDB connection
client =#
db = #
employee_details_collection = #
contracts_collection = #
templates_collection = #
contract_files_collection = #

@app.route('/create_contract', methods=['POST'])
def create_contract():
    data = request.json
    contract_type = data.get('contract_type')
    person_name = data.get('person_name')

    if not contract_type or not person_name:
        return jsonify({"error": "contract_type and person_name are required."}), 400

    # Check if a contract already exists for this person and contract type
    existing_contract = contracts_collection.find_one({"person_name": person_name, "template_name": contract_type})
    if existing_contract:
        return jsonify({"error": f"A {contract_type} contract already exists for {person_name}."}), 400

    # Fetch template based on contract_type
    template = templates_collection.find_one({"template_name": contract_type})
    if not template:
        return jsonify({"error": "Template not found."}), 404

    # Fetch employee details
    employee_details = employee_details_collection.find_one({"person_name": person_name})
    if not employee_details:
        return jsonify({"error": "Employee details not found."}), 404

    # Prepare contract data
    contract_data = {}
    pdf_data = {}
    missing_fields = []
    emp_details_field = []

    # Check common and specific fields in the template
    for field, status in {**template['common'], **template['specific']}.items():
        if status == "NA":
            continue
        if field in data:

            contract_data[field] = data[field]  # Use provided data first (override)
            pdf_data[field] = data[field]  # Include in PDF data
        elif field in employee_details:
            contract_data[field] = employee_details[field]
            emp_details_field.append(str(field) + " : " + str(employee_details[field]))
            pdf_data[field] = employee_details[field]  # Include in PDF data

        else:
            missing_fields.append(field)
    print("emp_details_field : ", emp_details_field)
    # Remove created_at and updated_at from the missing fields check
    missing_fields = [field for field in missing_fields if field not in ["created_at", "updated_at"]]

    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Add automatically generated fields
    contract_data["person_name"] = person_name
    contract_data["template_name"] = contract_type
    contract_data["created_at"] = datetime.utcnow()
    contract_data["updated_at"] = datetime.utcnow()

    # Add these fields to the PDF data as well
    pdf_data["person_name"] = person_name
    pdf_data["template_name"] = contract_type
    pdf_data["created_at"] = contract_data["created_at"]

    # Fetch and save the employee's email in the contract
    employee_email = employee_details.get("email")
    if employee_email:
        contract_data["email"] = employee_email
        pdf_data["email"] = employee_email  # Include in PDF data
    else:
        return jsonify({"error": "Employee email not found."}), 400

    # Save contract to the collection
    contract_id = contracts_collection.insert_one(contract_data).inserted_id

    # Convert ObjectId to string for JSON serialization
    contract_data["_id"] = str(contract_id)

    # Exclude certain fields from the PDF data
    pdf_data.pop("email", None)
    pdf_data.pop("template_name", None)
    pdf_data.pop("person_number", None)

    print()
    print("pdf_data : ",pdf_data)

    #pdf data will used to generate pdf using pdf generator fn also signs field will be added in pdf currently not added 
    # Generate PDF using the PDF generator (external function)
    #generated_pdf_path = generate_pdf(pdf_data)  # Assuming this function is provided externally and returns the file path of the generated PDF

    # generated_pdf_path=""
    # # Now, upload the generated PDF using the upload_file function
    # with open(generated_pdf_path, 'rb') as generated_pdf:
    #     response, status = upload_file(person_name, contract_type, generated_pdf)

    # Check if the PDF was uploaded successfully
    # if status != 201:
    #     return jsonify({"error": "Failed to upload the generated PDF.", "details": response}), status


    #data to send email
    email = {
        "person_name":person_name,
        "from_email":"CORE_HR_DEPARTMENT",
        "template_name":"Employment Contract",
        "data":pdf_data
    }
    print("Email data : ",email)

    return jsonify({"message": "Contract created successfully.", "contract": contract_data, "pdf_data": pdf_data}), 201

@app.route('/update_contract', methods=['POST'])
def update_contract():
    data = request.json
    person_name = data.get('person_name')
    contract_type = data.get('contract_type')

    if not person_name or not contract_type:
        return jsonify({"error": "person_name and contract_type are required."}), 400

    # Fetch the existing contract
    contract = contracts_collection.find_one({"person_name": person_name, "template_name": contract_type})
    if not contract:
        return jsonify({"error": "Contract not found."}), 404

    # Prepare updated data and update history
    updated_fields = {}
    pdf_data = {}

    # Fetch the existing contract data and populate pdf_data with existing values
    for key in contract:
        if key in ["_id", "created_at", "updated_at", "update_history"]:
            continue
        pdf_data[key] = contract[key]

    # Update the fields based on input data and add to pdf_data
    for key, value in data.items():
        if key not in ["person_name", "contract_type"]:
            updated_fields[key] = value
            pdf_data[key] = value

    if not updated_fields:
        return jsonify({"error": "No fields provided for update."}), 400

    # Update the contract and add to update history
    update_data = {
        "$set": updated_fields,
        "$push": {
            "update_history": {
                "updated_fields": updated_fields,
                "updated_at": datetime.utcnow(),
                "update_count": len(contract.get("update_history", [])) + 1
            }
        }
    }

    contracts_collection.update_one(
        {"person_name": person_name, "template_name": contract_type},
        update_data
    )
    # Exclude certain fields from the PDF data
    pdf_data.pop("email", None)
    pdf_data.pop("template_name", None)
    pdf_data.pop("person_number", None)

    #pdf data will used to generate pdf using pdf generator fn also signs field will be added in pdf currently not added 
    #pdf data will used to generate pdf using pdf generator fn also signs field will be added in pdf currently not added 
    # Generate PDF using the PDF generator (external function)
    #generated_pdf_path = generate_pdf(pdf_data)  # Assuming this function is provided externally and returns the file path of the generated PDF

    # generated_pdf_path=""
    # # Now, upload the generated PDF using the upload_file function
    # with open(generated_pdf_path, 'rb') as generated_pdf:
    #     response, status = upload_file(person_name, contract_type, generated_pdf)
    
    # Check if the PDF was uploaded successfully
    # if status != 201:
    #     return jsonify({"error": "Failed to upload the generated PDF.", "details": response}), status


    #data to send email
    email = {
        "person_name":person_name,
        "from_email":"CORE_HR_DEPARTMENT",
        "template_name":"Employment Contract",
        "data":pdf_data
    }
    print("Email data : ",email)

    return jsonify({"message": "Contract updated successfully.", "pdf_data": pdf_data}), 200



@app.route('/view_contract', methods=['POST'])    # For HR
def view_contract():
    data = request.json
    person_name = data.get('person_name')
    contract_type = data.get('contract_type')

    if not person_name:
        return jsonify({"error": "person_name is required."}), 400

    query = {"person_name": person_name}
    if contract_type:
        query["template_name"] = contract_type

    contracts = list(contracts_collection.find(query))
    if not contracts:
        return jsonify({"error": "No contracts found."}), 404

    # Convert ObjectId to string for JSON serialization
    for contract in contracts:
        contract["_id"] = str(contract["_id"])

    return jsonify({"contracts": contracts}), 200


@app.route('/upload_signed_pdf', methods=['POST'])
def upload_signed_pdf():
    # Check if file part is in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files['file']
    person_name = request.form.get('person_name')
    template_name = request.form.get('template_name')

    # Call the upload_file function with the provided input
    response, status = upload_file(person_name, template_name, file)
    
    return jsonify(response), status



def upload_file(person_name, template_name, file):
    # Ensure the upload folder exists before saving the file
    UPLOAD_FOLDER = 'uploads/'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create the folder if it doesn't exist

    # Validate file
    if file.filename == '':
        return {"error": "No selected file."}, 400

    # Validate person_name and template_name
    if not person_name or not template_name:
        return {"error": "person_name and template_name are required."}, 400

    # Check if the person and template exist in the HRM_employment_contracts collection
    contract_exists = contracts_collection.find_one({"person_name": person_name, "template_name": template_name})
    if not contract_exists:
        return {"error": f"No contract found for {person_name} with template {template_name}."}, 404

    # Check if a file for the same person and template already exists in the contract_files_collection
    existing_file = contract_files_collection.find_one({"person_name": person_name, "template_name": template_name, "file_name": secure_filename(file.filename)})
    if existing_file:
        return {"error": "File with the same name already exists. Please rename the file and try again."}, 400

    # Secure the filename
    filename = secure_filename(file.filename)

    # Save the file temporarily to the upload folder
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Prepare file data to be saved in MongoDB
    with open(file_path, 'rb') as f:
        file_data = {
            "person_name": person_name,
            "template_name": template_name,
            "file_name": filename,
            "file_content": f.read(),  # Read the content of the file
            "uploaded_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

    # Insert the file data into MongoDB
    contract_files_collection.insert_one(file_data)

    # Return success response
    return {"message": "File uploaded successfully.", "file_name": filename}, 201


    # Return a success message
    return jsonify({"message": "File uploaded successfully.", "file_name": filename}), 201





if __name__ == '__main__':
    app.run(debug=True)
