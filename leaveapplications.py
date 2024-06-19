from flask import Flask, request, jsonify
from pymongo import MongoClient, errors
import logging
import pymongo
from datetime import datetime, timedelta
from collections import Counter
from leave_accrual_config import leave_accrual_config




app = Flask(__name__)

def setup_routes(app):
    # MongoDB connection setup
    def get_mongo_connection():
        # Replace the connection string with your MongoDB connection string
        client = MongoClient("mongodb://localhost:27017/")  # Update this with your MongoDB connection string
        # Replace "your_database_name" with the actual database name
        db = client["company2"]
        return db

    # Function to get the current counter value or initialize it if it doesn't exist
    def get_counter(db):
        counter_collection = db["counter"]  # Collection to store the counter
        counter_doc = counter_collection.find_one({"_id": "person_number_counter"})
        if counter_doc:
            return counter_doc["value"]
        else:
            # Initialize counter if not exists
            counter_collection.insert_one({"_id": "person_number_counter", "value": 101})  # Starting from 102
            return 101

    # Function to increment and return the new counter value
    def increment_counter(db):
        counter_collection = db["counter"]  # Collection to store the counter
        new_counter_value = get_counter(db) + 1
        counter_collection.find_one_and_update(
            {"_id": "person_number_counter"},
            {"$set": {"value": new_counter_value}}
        )
        return new_counter_value

    # Function to flatten JSON data and insert into MongoDB
    def insert_data(db, data):
        # Remove the person number from the JSON data
        if "Person_Number" in data:
            del data["Person_Number"]

        # Get the current counter value and increment it
        counter = increment_counter(db)

        # Flatten the original data
        flattened_data = flatten_json(data, counter, db)

        # Convert date strings to date objects
        for key, value in flattened_data.items():
            if 'Date' in key and isinstance(value, str):
                try:
                    date_obj = datetime.strptime(value, "%Y-%m-%d").date()
                    flattened_data[key] = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    pass  # Keep the original value if conversion fails

        # Insert data into the collection
        collection = db["EmployeeDetails_UK"]
        collection.insert_one(flattened_data)
        print("Data inserted successfully")
        return "Data inserted successfully"

    # Function to flatten JSON data
    def flatten_json(data, counter, db):
        out = {}
        duplicates = Counter()  # Counter to keep track of duplicate fields

        def flatten(x, name=''):
            if isinstance(x, dict):
                for a in x:
                    if isinstance(x[a], dict):  # If the current field is a dictionary, go deeper without including the current key
                        flatten(x[a], name)
                    else:
                        field_name = name + a
                        if duplicates[field_name] == 0:  # Check if field is encountered for the first time
                            out[field_name] = x[a]
                        else:
                            # Field encountered more than once, ignore
                            print(f"Duplicate field: {field_name}")

                        duplicates[field_name] += 1
            else:
                if x:  # Only include non-empty values
                    out[name[:-1]] = x

        flatten(data)

        # Handling address separately
        address_keys = ['House_Number_Name', 'Street_Name', 'Town_City', 'Postcode']
        if all('Personal_Details_Address_' + key in out for key in address_keys):
            out['Address'] = ", ".join(out.pop('Personal_Details_Address_' + key) for key in address_keys)

        # Remove the nested prefixes
        cleaned_out = {}
        for key, value in out.items():
            cleaned_key = key.replace('Personal_Details_', '').replace('Employment_Details_', '').replace('Working_Hours_and_Shifts_', '')
            cleaned_out[cleaned_key] = value

        # Inserting person number
        cleaned_out['Person_Number'] = counter

        return cleaned_out

    @app.route('/processHrInfoUK', methods=['POST'])
    def process_hr_information():
        data = request.json
        if not data:
            return jsonify({"error": "Invalid data"}), 400

        db = get_mongo_connection()
        message = insert_data(db, data)
        return jsonify({"message": message}), 200
    
    
    db = get_mongo_connection()
    employees_collection = db["EmployeeDetails_UK"]
    leave_details_collection = db["Leave_Details"]
    leave_applications_collection = db["Leave_Applications"]

    @app.route('/applyForLeave', methods=['POST'])
    def submit_leave_application():
        data = request.json
        if not data:
            return jsonify({"error": "Invalid data"}), 400

        db = get_mongo_connection()
        if db is None:
            return jsonify({"error": "Could not connect to database"}), 500

        # Convert date strings to date objects
        try:
            if "Start_Date" in data:
                data["Start_Date"] = datetime.strptime(data["Start_Date"], "%Y-%m-%d").strftime("%Y-%m-%d")
            if "End_Date" in data:
                data["End_Date"] = datetime.strptime(data["End_Date"], "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError as e:
            logging.error(f"Date conversion error: {e}")
            return jsonify({"error": "Invalid date format"}), 400

        # Fetch the employee details
        employee_name = data.get("Employee_Name")
        if employee_name:
            name_parts = employee_name.split()
            if len(name_parts) < 2:
                return jsonify({"error": "Invalid Employee_Name. Please provide both first and last names."}), 400
            first_name = name_parts[0]
            last_name = name_parts[1]
        else:
            return jsonify({"error": "Employee_Name is required"}), 400

        employee_data = db["EmployeeDetails_UK"].find_one({"First_Name": first_name, "Last_Name": last_name})
        if not employee_data:
            return jsonify({"error": "Employee not found"}), 404

        person_number = employee_data["Person_Number"]

        # Prepare the document to be inserted
        leave_application = {
            "Person_Number": person_number,
            "Employee_Name": data["Employee_Name"],
            "Leave_Type": data.get("Leave_Type"),
            "Start_Date": data.get("Start_Date"),
            "End_Date": data.get("End_Date"),
            "Duration": data.get("Duration"),
            "Reason_for_Absence": data.get("Reason_for_Absence"),
            "Status": data.get("Status", "Pending"),
            "Manager": data.get("Manager", "Please provide your manager's name"),
            "Timestamp": datetime.now()
        }

        # Insert data into the Leave_Applications collection
        try:
            leave_applications_collection.insert_one(leave_application)
            logging.info("Leave application submitted successfully")

            # Insert entries into the Leave_Details collection for each day of absence
            start_date = datetime.strptime(data["Start_Date"], "%Y-%m-%d")
            end_date = datetime.strptime(data["End_Date"], "%Y-%m-%d")
            current_date = start_date
            while current_date <= end_date:
                leave_details_collection.insert_one({
                    "person_number": person_number,
                    "person_name": data["Employee_Name"],
                    "leave_type": data.get("Leave_Type", "absence"),
                    "date": current_date.strftime("%Y-%m-%d"),
                    "type": "Absence",
                    "days": -1,
                    "timestamp": datetime.now()
                })
                current_date += timedelta(days=1)

            # Automatically reduce the leave days from leave balances
            leave_type = data.get("Leave_Type", "annual_leave").replace(" ", "_").lower()
            leave_balance_record = db["Leave_Balances"].find_one({"person_number": person_number, "leave_type": leave_type})

            if leave_balance_record:
                new_balance = leave_balance_record["total_accrued_leave"] - data.get("Duration", 0)
                db["Leave_Balances"].update_one(
                    {"_id": leave_balance_record["_id"]},
                    {"$set": {"total_accrued_leave": new_balance, "timestamp": datetime.now()}}
                )
            else:
                # Insert a new leave balance record with negative balance
                new_balance = -data.get("Duration", 0)
                db["Leave_Balances"].insert_one({
                    "person_number": person_number,
                    "person_name": data["Employee_Name"],
                    "leave_type": leave_type,
                    "total_accrued_leave": new_balance,
                    "timestamp": datetime.now()
                })

            return jsonify({"message": "Leave application submitted successfully, and leave balance updated."}), 200
        except errors.PyMongoError as e:
            logging.error(f"Error inserting data: {e}")
            return jsonify({"error": f"Error inserting data: {e}"}), 500


 

    @app.route('/viewLeaveApplication', methods=['POST'])
    def view_leave_application():
        data = request.json
        if not data:
            return jsonify({"error": "Invalid data"}), 400

        db = get_mongo_connection()
        if db is None:
            return jsonify({"error": "Could not connect to database"}), 500

        query = {}
        
        # Adding filters based on the input data
        if "Employee_Name" in data:
            employee_name = data["Employee_Name"]
            name_parts = employee_name.split()
            if len(name_parts) < 2:
                return jsonify({"error": "Invalid Employee_Name. Please provide both first and last names."}), 400
            first_name = name_parts[0]
            last_name = name_parts[1]
            employee_data = db["EmployeeDetails_UK"].find_one({"First_Name": first_name, "Last_Name": last_name})
            if not employee_data:
                return jsonify({"error": "Employee not found"}), 404
            query["Person_Number"] = employee_data["Person_Number"]

        if "Leave_Type" in data:
            query["Leave_Type"] = data["Leave_Type"]

        if "Start_Date" in data:
            try:
                start_date = datetime.strptime(data["Start_Date"], "%Y-%m-%d")
                query["Start_Date"] = {"$gte": start_date.strftime("%Y-%m-%d")}
            except ValueError as e:
                logging.error(f"Date conversion error: {e}")
                return jsonify({"error": "Invalid date format for Start_Date"}), 400

        if "End_Date" in data:
            try:
                end_date = datetime.strptime(data["End_Date"], "%Y-%m-%d")
                query["End_Date"] = {"$lte": end_date.strftime("%Y-%m-%d")}
            except ValueError as e:
                logging.error(f"Date conversion error: {e}")
                return jsonify({"error": "Invalid date format for End_Date"}), 400

        try:
            collection = db["Leave_Applications"]
            leave_applications = collection.find(query)
            results = []
            for application in leave_applications:
                results.append({
                    "Person_Number": application["Person_Number"],
                    "Employee_Name": application["Employee_Name"],
                    "Leave_Type": application["Leave_Type"],
                    "Start_Date": application["Start_Date"],
                    "End_Date": application["End_Date"],
                    "Duration": application["Duration"],
                    "Reason_for_Absence": application["Reason_for_Absence"],
                    "Status": application["Status"],
                    "Manager": application["Manager"],
                    "Timestamp": application["Timestamp"]
                })
            
            if not results:
                return jsonify({"message": "No leave applications found"}), 404

            return jsonify({"leave_applications": results}), 200
        except errors.PyMongoError as e:
            logging.error(f"Error retrieving data: {e}")
            return jsonify({"error": f"Error retrieving data: {e}"}), 500
        
    @app.route('/editLeaveApplication', methods=['POST'])
    def edit_leave_application():
        data = request.json
        if not data:
            return jsonify({"error": "Invalid data"}), 400

        db = get_mongo_connection()
        if db is None:
            return jsonify({"error": "Could not connect to database"}), 500

        query = {}
        updates = {}

        # Adding filters based on the input data
        if "Employee_Name" in data:
            employee_name = data["Employee_Name"]
            name_parts = employee_name.split()
            if len(name_parts) < 2:
                return jsonify({"error": "Invalid Employee_Name. Please provide both first and last names."}), 400
            first_name = name_parts[0]
            last_name = name_parts[1]
            employee_data = db["EmployeeDetails_UK"].find_one({"First_Name": first_name, "Last_Name": last_name})
            if not employee_data:
                return jsonify({"error": "Employee not found"}), 404
            query["Person_Number"] = employee_data["Person_Number"]
        else:
            return jsonify({"error": "Employee_Name is required"}), 400

        if "Old_Leave_Type" in data:
            query["Leave_Type"] = data["Old_Leave_Type"]
        else:
            return jsonify({"error": "Old_Leave_Type is required"}), 400

        if "Old_Start_Date" in data:
            try:
                query["Start_Date"] = datetime.strptime(data["Old_Start_Date"], "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError as e:
                logging.error(f"Date conversion error: {e}")
                return jsonify({"error": "Invalid date format for Old_Start_Date"}), 400
        else:
            return jsonify({"error": "Old_Start_Date is required"}), 400

        if "Old_End_Date" in data:
            try:
                query["End_Date"] = datetime.strptime(data["Old_End_Date"], "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError as e:
                logging.error(f"Date conversion error: {e}")
                return jsonify({"error": "Invalid date format for Old_End_Date"}), 400
        else:
            return jsonify({"error": "Old_End_Date is required"}), 400

        # Check if the leave application status is pending
        leave_application = db["Leave_Applications"].find_one(query)
        if not leave_application:
            return jsonify({"error": "Leave application not found"}), 404
        if leave_application["Status"] != "Pending":
            return jsonify({"error": "Leave application is not pending and cannot be updated"}), 400

        # Adding updates based on the input data
        if "New_Start_Date" in data:
            try:
                updates["Start_Date"] = datetime.strptime(data["New_Start_Date"], "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError as e:
                logging.error(f"Date conversion error: {e}")
                return jsonify({"error": "Invalid date format for New_Start_Date"}), 400

        if "New_End_Date" in data:
            try:
                updates["End_Date"] = datetime.strptime(data["New_End_Date"], "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError as e:
                logging.error(f"Date conversion error: {e}")
                return jsonify({"error": "Invalid date format for New_End_Date"}), 400

        if "New_Leave_Type" in data:
            updates["Leave_Type"] = data["New_Leave_Type"]

        if "New_Reason_for_Absence" in data:
            updates["Reason_for_Absence"] = data["New_Reason_for_Absence"]

        if "New_Status" in data:
            updates["Status"] = data["New_Status"]

        if "New_Manager" in data:
            updates["Manager"] = data["New_Manager"]

        if not updates:
            return jsonify({"error": "No updates provided"}), 400

        try:
            collection = db["Leave_Applications"]
            result = collection.update_one(query, {"$set": updates})

            if result.matched_count == 0:
                return jsonify({"message": "No matching leave application found"}), 404

            logging.info("Leave application updated successfully")
            return jsonify({"message": "Leave application updated successfully"}), 200
        except errors.PyMongoError as e:
            logging.error(f"Error updating data: {e}")
            return jsonify({"error": f"Error updating data: {e}"}), 500

        
    

    @app.route('/LeaveBalances/edit', methods=['POST'])
    def modify_leave_balance():
        data = request.json
        if not data:
            return jsonify({"error": "Invalid data"}), 400

        db = get_mongo_connection()
        if db is None:
            return jsonify({"error": "Could not connect to database"}), 500

        employee_name = data.get("Employee_Name")
        modifications = data.get("Modifications")

        if not employee_name or not modifications:
            return jsonify({"error": "Missing Employee_Name or Modifications"}), 400

        # Split employee name into first and last names
        name_parts = employee_name.split()
        if len(name_parts) < 2:
            return jsonify({"error": "Invalid Employee_Name. Please provide both first and last names."}), 400
        first_name = name_parts[0]
        last_name = name_parts[1]

        # Fetch employee details
        employees_collection = db["EmployeeDetails_UK"]
        employee_data = employees_collection.find_one({"First_Name": first_name, "Last_Name": last_name})
        if not employee_data:
            return jsonify({"error": "Employee not found"}), 404

        person_number = employee_data["Person_Number"]

        collection = db["Leave_Balances"]

        for modification in modifications:
            leave_type = modification.get("Leave_Type")
            change = modification.get("Change")

            if not leave_type or change is None:
                return jsonify({"error": "Missing Leave_Type or Change in modifications"}), 400
            
            # Normalize leave_type by converting to lowercase and replacing spaces with underscores
            normalized_leave_type = leave_type.lower().replace(' ', '_')


            try:
                # Check if the leave type exists for the employee
                record = collection.find_one({"person_number": person_number, "leave_type": normalized_leave_type})

                if record:
                    # Update the existing leave balance
                    new_balance = record["total_accrued_leave"] + change
                    collection.update_one({"_id": record["_id"]}, {"$set": {"total_accrued_leave": new_balance}})
                    logging.info(f"Updated {leave_type} for {employee_name}, new balance: {new_balance}")
                else:
                    # Insert a new record for the leave type
                    new_record = {
                        "person_number": person_number,
                        "person_name": employee_name,
                        "leave_type": normalized_leave_type,
                        "total_accrued_leave": change,
                        "timestamp": datetime.now()
                    }
                    collection.insert_one(new_record)
                    logging.info(f"Inserted new {leave_type} for {employee_name} with balance: {change}")

            except errors.PyMongoError as e:
                logging.error(f"Error modifying data: {e}")
                return jsonify({"error": f"Error modifying data: {e}"}), 500

        return jsonify({"message": "Leave balances updated successfully"}), 200 
    



    @app.route('/LeaveBalances/view', methods=['POST'])  # Changed to GET
    def get_leave_balance():
        data = request.json
        if not data or "Employee_Name" not in data:
            return jsonify({"error": "Missing Employee_Name in request body"}), 400

        employee_name = data["Employee_Name"]

        db = get_mongo_connection()
        if db is None:
            return jsonify({"error": "Could not connect to database"}), 500

        employees_collection = db["EmployeeDetails_UK"]
        leave_accruals_collection = db["Leave_Balances"]

        try:
            # Find the employee's person number using their name
            employee_record = employees_collection.find_one({"First_Name": employee_name.split()[0], "Last_Name": employee_name.split()[1]})
            if not employee_record:
                return jsonify({"error": "No employee found with the specified name"}), 404

            person_number = employee_record["Person_Number"]

            # Find leave balances for the employee using their person number
            records = leave_accruals_collection.find({"person_number": person_number})
            leave_balances = []
            for record in records:
                leave_balances.append({
                    "Leave_Type": record["leave_type"],
                    "Leave_Balance": record["total_accrued_leave"]
                })

            if not leave_balances:
                return jsonify({"error": "No leave balances found for the specified employee"}), 404

            return jsonify({"employee_name": employee_name, "leave_balances": leave_balances}), 200
        except errors.PyMongoError as e:
            logging.error(f"Error retrieving data: {e}")
            return jsonify({"error": f"Error retrieving data: {e}"}), 500
        
    db = get_mongo_connection()
    employees_collection = db["EmployeeDetails_UK"]
    leave_accruals_collection = db["Leave_Balances"]
    leave_details_collection = db["Leave_Details"]
        

    def calculate_leave_accrual(start_date, end_date, employee_type, leave_type, gender=None, fte=1.0, additional_leave_rate=0.0):
        # Input validation
        if not (start_date and end_date and employee_type and leave_type):
            return {"error": "Invalid input parameters"}

        # Check if leave type exists in the configuration
        leave_type_details = leave_accrual_config["leave_types"].get(leave_type)
        if not leave_type_details:
            return {"error": "Invalid leave type"}

        # Check if leave type is applicable based on gender
        if "applicable_gender" in leave_type_details and leave_type_details["applicable_gender"] != gender:
            return {"error": "Leave type not applicable based on gender"}

        # Get the accrual rate for the given employee type and leave type
        accrual_rate = leave_type_details["accrual_rates"].get(employee_type)
        if accrual_rate is None:
            return {"error": "Invalid employee type"}

        # Prorate accrual rate based on FTE for part-time employees
        prorated_accrual_rate = accrual_rate * fte if employee_type == "part-time" else accrual_rate

        # Calculate the number of months between start_date and end_date
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Initialize total accrued leave
        total_accrued_leave = 0.0

        # Calculate the number of full months between start_date and end_date
        # while start_date <= end_date:
            # Add the prorated accrual rate plus additional leave rate to the total accrued leave
        total_accrued_leave += prorated_accrual_rate + additional_leave_rate

            # Move to the next month
        start_date = start_date.replace(day=1) + timedelta(days=32)
        start_date = start_date.replace(day=1)

        return {"total_accrued_leave": total_accrued_leave}

    def calculate_leave_accrual1(start_date, end_date, employee_type, leave_type, gender=None, fte=1.0, additional_leave_rate=0.0):
        # Input validation
        if not (start_date and end_date and employee_type and leave_type):
            return {"error": "Invalid input parameters"}

        # Check if leave type exists in the configuration
        leave_type_details = leave_accrual_config["leave_types"].get(leave_type)
        if not leave_type_details:
            return {"error": "Invalid leave type"}

        # Check if leave type is applicable based on gender
        if "applicable_gender" in leave_type_details and leave_type_details["applicable_gender"] != gender:
            return {"error": "Leave type not applicable based on gender"}

        # Get the accrual rate for the given employee type and leave type
        accrual_rate = leave_type_details["accrual_rates"].get(employee_type)
        if accrual_rate is None:
            return {"error": "Invalid employee type"}

        # Prorate accrual rate based on FTE for part-time employees
        prorated_accrual_rate = accrual_rate * fte if employee_type == "part-time" else accrual_rate

        # Calculate the number of months between start_date and end_date
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Initialize total accrued leave
        total_accrued_leave = 0.0

        # Calculate the number of full months between start_date and end_date
        while start_date <= end_date:
            # Add the prorated accrual rate plus additional leave rate to the total accrued leave
            total_accrued_leave += prorated_accrual_rate + additional_leave_rate

            # Move to the next month
            start_date = start_date.replace(day=1) + timedelta(days=32)
            start_date = start_date.replace(day=1)

        return {"total_accrued_leave": total_accrued_leave}

    def calculate_leave_accrual2(start_date, end_date, employee_type, leave_type, gender=None, fte=1.0, additional_leave_rate=0.0):
        # Input validation
        if not (start_date and end_date and employee_type and leave_type):
            return {"error": "Invalid input parameters"}

        # Check if leave type exists in the configuration
        leave_type_details = leave_accrual_config["leave_types"].get(leave_type)
        if not leave_type_details:
            return {"error": "Invalid leave type"}

        # Check if leave type is applicable based on gender
        if "applicable_gender" in leave_type_details and leave_type_details["applicable_gender"] != gender:
            return {"error": "Leave type not applicable based on gender"}

        # Get the accrual rate for the given employee type and leave type
        accrual_rate = leave_type_details["accrual_rates"].get(employee_type)
        if accrual_rate is None:
            return {"error": "Invalid employee type"}

        # Prorate accrual rate based on FTE for part-time employees
        prorated_accrual_rate = accrual_rate * fte if employee_type == "part-time" else accrual_rate

        # Calculate the number of months between start_date and end_date
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Initialize total accrued leave
        total_accrued_leave = 0.0

        # Calculate the number of full months between start_date and end_date
        while start_date <= end_date:
            # Add the prorated accrual rate plus additional leave rate to the total accrued leave
            total_accrued_leave = prorated_accrual_rate + additional_leave_rate

            # Move to the next month
            start_date = start_date.replace(day=1) + timedelta(days=32)
            start_date = start_date.replace(day=1)

        return {"total_accrued_leave": total_accrued_leave}


    def insert_monthly_leave_details(person_number, person_name, start_date, end_date, leave_type, days_per_month):
        """
        Insert monthly leave details for each month from start_date to end_date.

        Parameters:
            person_number (str): The person number of the employee.
            person_name (str): The name of the employee.
            start_date (str): The start date in the format "YYYY-MM-DD".
            end_date (str): The end date in the format "YYYY-MM-DD".
            leave_type (str): The type of leave.
            days_per_month (float): The number of days accrued per month.
        """
        # Convert strings to datetime
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Iterate through each month
        while start_date <= end_date:
            leave_details_collection.insert_one({
                "person_number": person_number,
                "person_name": person_name,
                "leave_type": leave_type,
                "date": start_date.strftime("%Y-%m-%d"),
                "type": "Monthly Leave Accruals",
                "days": days_per_month["total_accrued_leave"],
                "timestamp": datetime.now()
            })
            # Move to the next month
            start_date = start_date.replace(day=1) + timedelta(days=32)
            start_date = start_date.replace(day=1)



    def calculate_additional_leave_rate(seniority_level, shift_type):
        # Get additional leave rate based on seniority level and shift type
        seniority_leave_rate = leave_accrual_config.get("seniority_levels", {}).get(seniority_level, {}).get("additional_leave_rate", 0.0)
        shift_leave_rate = leave_accrual_config.get("shift_types", {}).get(shift_type, {}).get("additional_leave_rate", 0.0)
        print("shift_leave_rate1:", shift_leave_rate)

        # Combine both leave rates
        return seniority_leave_rate + shift_leave_rate


    def calculate_seniority_level(start_date, hire_date):
        # Convert strings to datetime if they are not already
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if isinstance(hire_date, str):
            hire_date = datetime.strptime(hire_date, "%Y-%m-%d")
        years_of_service = (start_date - hire_date).days / 365
        if years_of_service < 5:
            return "1-5"
        elif years_of_service < 10:
            return "6-10"
        else:
            return "10+"


    def get_unionized_leave_accrual(employment_type, fte, union_name):
        # Get accrual rates for unionized employees based on employment type
        accrual_rates = leave_accrual_config.get("unionized_employees", {}).get(union_name, {}).get("accrual_rates", {})
        accrual_rate = accrual_rates.get(employment_type, 0.0)

        # Prorate accrual rate based on FTE for part-time employees
        if employment_type == "part-time":
            accrual_rate *= fte

        return accrual_rate


    @app.route('/calculate_leave_accruals', methods=['POST'])
    def calculate_leave_accruals_endpoint():
        data = request.json

        person_name = data.get("person_name")
        business_unit = data.get("business_unit")
        legal_entity = data.get("legal_entity")
        
        # Split person_name into first and last names
        if person_name:
            name_parts = person_name.split()
            if len(name_parts) < 2:
                return jsonify({"error": "Invalid person_name. Please provide both first and last names."}), 400
            first_name = name_parts[0]
            last_name = name_parts[1]
        else:
            first_name = None
            last_name = None
        
        # Build the query based on the provided filters
        query = {}
        if first_name and last_name:
            query["First_Name"] = first_name
            query["Last_Name"] = last_name
        if business_unit:
            query["Business_Unit"] = business_unit
        if legal_entity:
            query["Legal_Entity"] = legal_entity

        # Fetch all matching employees
        matching_employees = employees_collection.find(query)

        # Check if multiple employees with the same name exist
        employees = list(matching_employees)
        if not employees:
            return jsonify({"error": "No employees found for the provided criteria"}), 404

        if len(employees) > 1 and not (business_unit and legal_entity):
            return jsonify({"error": "Multiple employees found with the same name. Please provide additional details such as Person_Number, Business_Unit, or Legal_Entity."}), 400

        for employee_data in employees:
            person_number = employee_data["Person_Number"]
            
            # Check existing leave records for the employee
            existing_record = leave_accruals_collection.find_one({"person_number": person_number})
            
            # Extract relevant data for leave accrual calculation
            start_date = datetime.strptime(employee_data["Original_Start_Date"], "%Y-%m-%d")
            hire_date = datetime.strptime(employee_data["Hire_Date"], "%Y-%m-%d")
            gender = employee_data["Gender"]
            employment_type = employee_data["Employment_Type"].lower()
            fte = float(employee_data["FTE"])

            # Use financial year start date if hire date is after financial year start date, else use hire date
            current_year = datetime.now().year
            financial_year_start = datetime(current_year, 4, 1)
            start_date = max(start_date, hire_date, financial_year_start).strftime("%Y-%m-%d")
            end_date = datetime.utcnow().strftime("%Y-%m-%d")  # Use current date as end date

            # Fetch shift details for the employee
            shift_type = employee_data.get("Shift_Type", "")  # Assume the field in MongoDB is "Shift_Type"
            seniority_level = calculate_seniority_level(end_date, hire_date)  # Calculate seniority level based on hire date
            union_name = employee_data.get("Union_Name", "")
            union_member = employee_data.get("Union_Member", False)  # Check if employee is a union member
            unionized_leave_accrual = get_unionized_leave_accrual(employment_type, fte, union_name) if union_member else 0.0

            # Perform leave accrual calculation for all leave types
            for leave_type in ["annual_leave"]:
                # Calculate additional leave accrual based on seniority level and shift type
                additional_leave_rate = calculate_additional_leave_rate(seniority_level, shift_type) + unionized_leave_accrual
                accrued_leave = calculate_leave_accrual(start_date, end_date, employment_type, leave_type, gender, fte, additional_leave_rate)
                accrued_leave1 = calculate_leave_accrual1(start_date, end_date, employment_type, leave_type, gender, fte, additional_leave_rate)
                days_per_month = calculate_leave_accrual2(start_date, end_date, employment_type, leave_type, gender, fte, additional_leave_rate)

                # Update or insert leave accrual data in the MongoDB collection
                if existing_record:
                    last_update = existing_record["timestamp"]
                    if (datetime.now() - last_update).days > 30:
                        new_total_accrued_leave = existing_record["total_accrued_leave"] + accrued_leave["total_accrued_leave"]
                        leave_accruals_collection.update_one(
                            {"person_number": person_number},
                            {"$set": {
                                "total_accrued_leave": new_total_accrued_leave,
                                "timestamp": datetime.now()
                            }}
                        )
                        leave_details_collection.insert_one({
                            "person_number": person_number,
                            "person_name": employee_data["First_Name"] + " " + employee_data["Last_Name"],
                            "leave_type": leave_type,
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "type": "Monthly Leave Accruals",
                            "days": accrued_leave["total_accrued_leave"],
                            "timestamp": datetime.now()
                        })
                else:
                    leave_record = {
                        "person_number": person_number,
                        "person_name": employee_data["First_Name"] + " " + employee_data["Last_Name"],
                        "leave_type": leave_type,
                        "total_accrued_leave": accrued_leave1["total_accrued_leave"],
                        "timestamp": datetime.now()
                    }
                    leave_accruals_collection.insert_one(leave_record)
                    insert_monthly_leave_details(person_number, person_name, start_date, end_date, leave_type, days_per_month)

        return jsonify({"message": "Leave accruals calculated and stored successfully"}), 200