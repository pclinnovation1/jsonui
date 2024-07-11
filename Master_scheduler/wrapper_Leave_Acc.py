from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
from leave_accrual_config import leave_accrual_config

app = Flask(__name__)

# MongoDB connection setup
client = MongoClient("mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns")
db = client["PCL_Interns"]
employees_collection = db["S_EmployeeDetails_UK"]
leave_accruals_collection = db["S_Leave_Balances"]
leave_details_collection = db["S_Leave_Details"]


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


def update_or_insert_leave_accrual(person_number):
    # Fetch employee data based on person_number
    employee_data = employees_collection.find_one({"Person_Number": person_number})

    if not employee_data:
        return {"error": f"No employee found with person number {person_number}"}
    
    # Get the full name from First_Name and Last_Name
    person_name = f"{employee_data['First_Name']} {employee_data['Last_Name']}"
        
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
            last_update = existing_record["last_accrued_leave"]
            if (datetime.now() - last_update).days > 30:
                new_total_accrued_leave = existing_record["total_accrued_leave"] + accrued_leave["total_accrued_leave"]
                leave_accruals_collection.update_one(
                    {"person_number": person_number},
                    {"$set": {
                        "total_accrued_leave": new_total_accrued_leave,
                        "last_accrued_leave": datetime.now()
                    }}
                )
                leave_details_collection.insert_one({
                    "person_number": person_number,
                    "person_name": employee_data["First_Name"] + " " + employee_data["Last_Name"],
                    "leave_type": leave_type,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "type": "Monthly Leave Accruals",
                    "days": accrued_leave["total_accrued_leave"],
                    "last_accrued_leave": datetime.now()
                })
            else:
                return jsonify({"message": "Leave has been already accured for this month"}), 200
        else:
            leave_record = {
                "person_number": person_number,
                "person_name": employee_data["First_Name"] + " " + employee_data["Last_Name"],
                "leave_type": leave_type,
                "total_accrued_leave": accrued_leave1["total_accrued_leave"],
                "last_accrued_leave": datetime.now()
            }
            leave_accruals_collection.insert_one(leave_record)
            insert_monthly_leave_details(person_number, person_name, start_date, end_date, leave_type, days_per_month)

    return jsonify({"message": "Leave accruals calculated and stored successfully"}), 200