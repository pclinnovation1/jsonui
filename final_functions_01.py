from pymongo import MongoClient
from datetime import datetime, timedelta
from dateutil import parser
import config  # Import the configuration file
import pandas as pd
import numpy as np
import re, math

# from final_functions_02 import fetch_latest_salary_update, fetch_annual_salary

# MongoDB connection utility
def get_mongo_connection(uri=config.MONGO_URI):
    """
    Establishes a connection to the MongoDB database.

    Parameters:
    uri (str): The MongoDB URI for connection.

    Returns:
    MongoClient: A MongoClient object to interact with the MongoDB database.
    """
    return MongoClient(uri)

# Initialize MongoDB connection and database outside the functions
client = get_mongo_connection()
db = client[config.DATABASE_NAME]

# Define collections outside the functions for easy access
absence_details_collection = db[config.COLLECTIONS['absence_details']]
nic_employee_config_collection = db[config.COLLECTIONS['nic_config_employee']]
nic_employer_config_collection = db[config.COLLECTIONS['nic_config_employer']]
pension_config_collection = db[config.COLLECTIONS['pension_config']]
student_loan_config_collection = db[config.COLLECTIONS['student_config']]
salary_details_collection = db[config.COLLECTIONS['salary_details']]
smp_config_collection = db[config.COLLECTIONS['smp_config']]
tax_config_collection = db[config.COLLECTIONS['tax_config']]

# balance_calculation_report_collection = db[config.COLLECTIONS['balance_calculation_report']]
# employee_information_collection = db[config.COLLECTIONS['employee_information']]
# migration_data_collection = db[config.COLLECTIONS['migration_data']]
# pension_details_collection = db[config.COLLECTIONS['pension_details']]
# tax_codes_collection = db[config.COLLECTIONS['tax_codes']]

# -----------------------------------------------------------------------------------------------------------

def fetch_latest_salary_update(emp_num, end_date, payroll_process_date, client_id):
    """
    Fetch the latest salary update for a given employee number, end date, payroll process date, and client ID.
    
    Parameters:
    - emp_num (str or int): Employee number.
    - end_date (str): End date (format: 'YYYY-MM-DD HH:MM:SS').
    - payroll_process_date (str): Payroll process date (format: 'YYYY-MM-DD HH:MM:SS').
    - client_id (str): Client identifier.
    
    Returns:
    - datetime or None: Latest salary creation date, or None if no record is found.
    """

    # Convert end_date and payroll_process_date to datetime objects if they are strings
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
    if isinstance(payroll_process_date, str):
        payroll_process_date = datetime.strptime(payroll_process_date, '%Y-%m-%d %H:%M:%S')

    # Query MongoDB to fetch the latest salary update
    query = {
        "EMPLOYEE_NUMBER": emp_num,
        "EFFECTIVE_START_DATE": {"$lte": end_date},
        "SALARY_CREATION_DATE": {"$lte": payroll_process_date},
        "CLIENT_ID": client_id
    }

    # Sort the results by EFFECTIVE_START_DATE in descending order and get the first record
    result = list(salary_details_collection.find(query).sort("EFFECTIVE_START_DATE", -1).limit(1))

    latest_salary_date = None
    if len(result) > 0:
        latest_salary_date = result[0].get('SALARY_CREATION_DATE')
        # Convert the date from MongoDB to datetime object if it is in string format
        if isinstance(latest_salary_date, str):
            latest_salary_date = datetime.strptime(latest_salary_date, '%Y-%m-%d %H:%M:%S')

    return latest_salary_date

# # Test cases for fetch_latest_salary_update function
# print("Test Case 1: Valid employee number and dates")
# print("Expected output: A datetime object representing the latest salary creation date")
# print("Actual output:", fetch_latest_salary_update(104, '2023-06-30 00:00:00', '2023-06-15 00:00:00', 'Bansal Groups_22_03_2024'), "\n")

# print("Test Case 2: Employee number with no matching records")
# print("Expected output: None")
# print("Actual output:", fetch_latest_salary_update(999, '2023-06-30 00:00:00', '2023-06-15 00:00:00', 'Bansal Groups_22_03_2024'), "\n")

# print("Test Case 3: Invalid date formats")
# print("Expected output: None or an error if date parsing fails")
# print("Actual output:", fetch_latest_salary_update(104, 'invalid_date', 'invalid_date', 'Bansal Groups_22_03_2024'), "\n")

# ---------------------------------------------------------------------------------------------------------------

def fetch_annual_salary(emp_num, sal_last_update_date, client_id):
    """
    Fetches the annual salary for the given employee number and salary creation date from MongoDB.
    
    Parameters:
    - emp_num (str or int): The employee number.
    - sal_last_update_date (str): The salary creation date as a string in the format '%Y-%m-%d %H:%M:%S'.
    - client_id (str): The client ID.

    Returns:
    - float: The annual salary or 0.0 if no record is found.
    """

    # Convert sal_last_update_date to datetime if it is a string
    if isinstance(sal_last_update_date, str):
        sal_last_update_date = datetime.strptime(sal_last_update_date, '%Y-%m-%d %H:%M:%S')

    # Query MongoDB to fetch the annual salary
    query = {
        "EMPLOYEE_NUMBER": emp_num,  # Ensure employee number is treated as a string
        "SALARY_CREATION_DATE": sal_last_update_date.strftime('%Y-%m-%d %H:%M:%S'),  # Ensure date format is string
        "CLIENT_ID": client_id
    }
    

    # Sort the results by EFFECTIVE_START_DATE in descending order and get the first record
    # result = list(salary_details_collection.find(query).sort("EFFECTIVE_START_DATE", -1).limit(1))
    result = list(salary_details_collection.find(query))
    # print("query: ", query)
    # print()
    # print("length of result: ",len(result))
    # print()

    annual_salary = 0.0
    if len(result) > 0:
        # Extract ANNUAL_SALARY from the document
        annual_salary = result[0].get('ANNUAL_SALARY', 0.0)

        # Ensure it's a float
        if not isinstance(annual_salary, float):
            annual_salary = float(annual_salary)

    return annual_salary

# # Test cases for fetch_annual_salary function
# print("Test Case 1: Valid employee number and dates")
# print("Expected output: A float value representing the annual salary")
# print("Actual output:", fetch_annual_salary(104, '2023-04-03 00:00:00', 'Bansal Groups_22_03_2024'), "\n")

# print("Test Case 2: Employee number with no matching records")
# print("Expected output: 0.0")
# print("Actual output:", fetch_annual_salary(999, '2023-04-03 00:00:00', 'Bansal Groups_22_03_2024'), "\n")

# print("Test Case 3: Invalid date format")
# print("Expected output: Error due to invalid date format")
# try:
#     print("Actual output:", fetch_annual_salary(104, 'invalid_date', 'Bansal Groups_22_03_2024'), "\n")
# except Exception as e:
#     print(f"Error: {e}")

# ----------------------------------------------------------------------------------------------------------



















# ------------------------------------------------------------------------------------------------

def uk_ps_absence_entitlement_days_1(emp_num, start, end, payroll_process_date, client_id):
    """
    Calculates the total days of absence entitlement for Annual Leave from MongoDB.

    Parameters:
    emp_num (str): The employee number.
    start (datetime): The start date of the absence period.
    end (datetime): The end date of the absence period.
    payroll_process_date (datetime): The date of the payroll process.
    client_id (str): The client identifier.

    Returns:
    float: Total days of absence entitlement.
    """
    total_days = 0
    print("absence_details_collection: ", absence_details_collection)
    print()

    # Convert payroll_process_date to string if it's a datetime object
    if isinstance(payroll_process_date, str):
        payroll_process_date_str = payroll_process_date  # Already a string
    else:
        payroll_process_date_str = payroll_process_date.strftime('%Y-%m-%d %H:%M:%S')

    # Fetch absence details
    query = {
        'EMPLOYEE_ID': emp_num,  # Ensure this is a string if the database field is a string
        'LEAVE_TYPE': 'Annual Leave',
        'LAST_UPDATE_DATE': {'$lt': payroll_process_date_str},  # Convert to string
        'CLIENT_ID': client_id
    }
    print("Querying MongoDB with:", query)

    projection = {
        "LEAVE_START_DATE_TIME": 1,
        "LEAVE_END_DATE_TIME": 1
    }

    absence_details = list(absence_details_collection.find(query, projection))

    print("absence_details: ", absence_details)

    # Convert cursor to list to print and debug
    absence_details_list = list(absence_details)
    print("Fetched records:", absence_details_list)

    for record in absence_details_list:
        print("Processing record:", record)

        leave_start = record['LEAVE_START_DATE_TIME']
        leave_end = record['LEAVE_END_DATE_TIME']
        print(f"Original leave_start: {leave_start}, leave_end: {leave_end}")

        # Properly parse dates using dateutil parser
        leave_start = parser.parse(leave_start).date()  # Ignore time
        leave_end = parser.parse(leave_end).date()      # Ignore time
        print(f"Parsed leave_start: {leave_start}, leave_end: {leave_end}")

        # Check if start and end dates are the same
        if leave_start == leave_end:
            print("Leave start and end dates are the same, counting as 1 full day leave.")
            total_days += 1
            continue

        # Calculate the number of full days between start and end dates
        absence_start = max(leave_start, start.date())  # Convert start to date
        absence_end = min(leave_end, end.date())        # Convert end to date
        print(f"Calculated absence_start: {absence_start}, absence_end: {absence_end}")

        if absence_start > absence_end:
            print("Skipping record due to absence_start > absence_end")
            continue

        # Calculate the duration in full days
        absence_duration_days = (absence_end - absence_start).days + 1
        print(f"Calculated absence_duration_days: {absence_duration_days} days")

        total_days += absence_duration_days
        print(f"Updated total_days: {total_days}")

    return total_days

# Test cases with direct input
# print("Test Case 1: Normal Case with Absences Within Period")
# print("Expected output: Dependent on MongoDB records")
# print("Total Absence Days:", uk_ps_absence_entitlement_days_1("113", datetime(2024, 1, 1), datetime(2024, 12, 31), datetime(2024, 2, 27), "Bansal Groups_22_03_2024"), "\n")

# print("Test Case 2: Normal Case with Absences Within Period")
# print("Expected output: Dependent on MongoDB records")
# print("Total Absence Days:", uk_ps_absence_entitlement_days_1("104", datetime(2024, 1, 1), datetime(2024, 12, 31), datetime(2024, 2, 27), "Bansal Groups_22_03_2024"), "\n")


# -------------------------------------------------------------------------------------------------


def uk_ps_absence_entitlement_days(emp_num, start, end, payroll_process_date, client_id):
    total_days = 0

    # Query MongoDB to fetch absence details
    absence_details = absence_details_collection.find({
        "EMPLOYEE_ID": emp_num,
        "LEAVE_TYPE": "GB Paternity Leave",
        "LAST_UPDATE_DATE": {"$lt": payroll_process_date},
        "CLIENT_ID": client_id
    }, {"LEAVE_START_DATE_TIME": 1, "LEAVE_END_DATE_TIME": 1})

    for record in absence_details:
        leave_start = record['LEAVE_START_DATE_TIME']
        leave_end = record['LEAVE_END_DATE_TIME']

        # Convert date strings to datetime objects if they are not already
        if isinstance(leave_start, str):
            leave_start = parser.parse(leave_start)
        if isinstance(leave_end, str):
            leave_end = parser.parse(leave_end)

        absence_start = max(leave_start, start)
        absence_end = min(leave_end, end)

        if absence_start > absence_end:
            continue

        absence_interval = absence_end - absence_start
        absence_duration = absence_interval.days + absence_interval.seconds / (24 * 3600)

        if leave_start.month == leave_end.month:
            total_days += absence_duration
        else:
            if int(absence_duration) == absence_duration:
                total_days += (absence_end - absence_start).days + 1
            else:
                total_days += (absence_end - absence_start).days + absence_duration % 1

    return total_days

# Test cases with direct input

# print("Test Case 1: Normal Case with Absences Within Period")
# print("Expected output: Dependent on MongoDB records")
# print("Total Absence Days:", uk_ps_absence_entitlement_days("104", datetime(2024, 1, 1), datetime(2024, 12, 31), "2024-02-27", "Bansal Groups_22_03_2024"), "\n")

# ------------------------------------------------------------------------------------------------

from datetime import datetime, timedelta

def uk_ps_ytd_absence_entitlement_2(v_emp_num, p_ytd_start_date, p_ytd_end_date, v_payroll_process_date, v_client_id):
    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return datetime.strptime(date_str, '%Y-%m-%d')

    # Parse dates with the possibility of missing time parts
    v_ytd_start_date = parse_date(p_ytd_start_date)
    v_ytd_end_date = parse_date(p_ytd_end_date)
    v_payroll_process_date = parse_date(v_payroll_process_date)
    v_current_date = v_ytd_start_date.replace(day=1)

    v_total_ytd_absence_entitlement = 0

    while v_current_date <= v_ytd_end_date.replace(day=1):
        v_start_date = v_current_date.replace(day=1)
        v_end_date = (v_current_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        # Fetch the latest salary update
        v_sal_last_update_date = fetch_latest_salary_update(v_emp_num, v_end_date.strftime('%Y-%m-%d %H:%M:%S'), v_payroll_process_date, v_client_id)
        
        if v_sal_last_update_date is None:
            print(f"No salary update found for employee {v_emp_num}. Skipping this period.")
            v_current_date = v_current_date.replace(day=1) + timedelta(days=32)
            continue
        
        # Fetch the annual salary
        v_annual_salary = fetch_annual_salary(v_emp_num, v_sal_last_update_date, v_client_id)

        if v_ytd_end_date.month == v_end_date.month:
            v_absence_entitlement_days = uk_ps_absence_entitlement_days_1(v_emp_num, v_start_date.strftime('%Y-%m-%d %H:%M:%S'), v_end_date.strftime('%Y-%m-%d %H:%M:%S'), v_payroll_process_date, v_client_id)
        else:
            v_absence_entitlement_days = uk_ps_absence_entitlement_days(v_emp_num, v_start_date.strftime('%Y-%m-%d %H:%M:%S'), v_end_date.strftime('%Y-%m-%d %H:%M:%S'), v_payroll_process_date, v_client_id)

        v_monthly_absence_entitlement = (v_absence_entitlement_days * v_annual_salary / 260)
        v_total_ytd_absence_entitlement += v_monthly_absence_entitlement

        v_current_date = v_current_date.replace(day=1) + timedelta(days=32)
    
    return v_total_ytd_absence_entitlement

# # Test cases for uk_ps_ytd_absence_entitlement_2 function
# print("Test Case 1: Employee 104")
# print("Expected output: Calculated YTD absence entitlement")
# print("Actual output:", uk_ps_ytd_absence_entitlement_2(104, '2024-04-01', '2024-05-31 23:59:59', '2024-05-30 00:00:00', 'Bansal Groups_22_03_2024'), "\n")

# print("Test Case 2: Employee 105")
# print("Expected output: Calculated YTD absence entitlement")
# print("Actual output:", uk_ps_ytd_absence_entitlement_2('105', '2024-01-01 00:00:00', '2024-12-31 23:59:59', '2024-02-27 00:00:00', 'Bansal Groups_22_03_2024'), "\n")

# print("Test Case 3: Employee 106")
# print("Expected output: Calculated YTD absence entitlement")
# print("Actual output:", uk_ps_ytd_absence_entitlement_2('106', '2024-01-01', '2024-12-31 23:59:59', '2024-02-27 00:00:00', 'Bansal Groups_22_03_2024'), "\n")


# ------------------------------------------------------------------------------------------------

def uk_ps_add_working_days(start_date, num_workdays):
    result_date = start_date
    counter = 0

    while counter < num_workdays:
        result_date += timedelta(days=1)  # Increment the date by one day

        # Check if the resulting date is a workday (Monday to Friday)
        while result_date.weekday() >= 5:  # 5 for Saturday and 6 for Sunday
            result_date += timedelta(days=1)  # If it's a weekend, move to the next day

        counter += 1  # Increment the counter for each workday

    return result_date

# Test cases with direct input

# print("Test Case 1: Start on a Monday, add 5 workdays")
# print("Expected output: Following Monday")
# print("Result Date:", uk_ps_add_working_days(datetime(2024, 9, 1), 5), "\n")  

# print("Test Case 2: Start on a Friday, add 1 workday")
# print("Expected output: Following Monday")
# print("Result Date:", uk_ps_add_working_days(datetime(2024, 9, 5), 1), "\n")  

# print("Test Case 3: Start on a Thursday, add 10 workdays")
# print("Expected output: Thursday after next week")
# print("Result Date:", uk_ps_add_working_days(datetime(2024, 9, 4), 10), "\n")  

# ----------------------------------------------------------------------------------------


def calculate_cost_to_employer(gross_pay, nic_tax_employer, pension_contribution_employer):
    """
    Calculates the total cost to the employer.

    Parameters:
    gross_pay (float): Gross pay of the employee.
    nic_tax_employer (float): Employer's National Insurance Contributions.
    pension_contribution_employer (float): Employer's pension contributions.

    Returns:
    float: Total cost to the employer.
    """
    cost_to_employer = gross_pay + nic_tax_employer + pension_contribution_employer
    return cost_to_employer

def calculate_net_income(gross_pay, nic_tax_employee, tax_normal, student_loan_repayment):
    """
    Calculates the net income of the employee.

    Parameters:
    gross_pay (float): Gross pay of the employee.
    nic_tax_employee (float): Employee's National Insurance Contributions.
    tax_normal (float): Normal tax deducted from the employee's salary.
    student_loan_repayment (float): Student loan repayment deducted from the employee's salary.

    Returns:
    float: Net income of the employee.
    """
    net_income = gross_pay - nic_tax_employee - tax_normal - student_loan_repayment
    return net_income

# # Test cases for calculate_cost_to_employer
# print("Test Case 1: calculate_cost_to_employer")
# print("Expected output: 7000")
# print("Actual output:", calculate_cost_to_employer(5000, 1000, 1000), "\n")

# # Test cases for calculate_net_income
# print("Test Case 1: calculate_net_income")
# print("Expected output: 3000")
# print("Actual output:", calculate_net_income(5000, 1000, 800, 200), "\n")


# ---------------------------------------------------------------------------

def fetch_nic_config_from_mongodb(nic_category):
    """
    Fetch NIC configuration from MongoDB for the given NIC category.

    Parameters:
    nic_category (str): The NIC category (e.g., 'A', 'B', etc.)

    Returns:
    dict: A dictionary containing NIC configuration details.
    """
    config = nic_employee_config_collection.find_one({"NIC_Category": nic_category})
    return config

def calculate_nic_tax_employee_2024(gross_pay, nic_category='A'):
    """
    Calculate NIC tax for an employee for 2024 based on gross pay and NIC category.

    Parameters:
    gross_pay (float): The gross pay of the employee.
    nic_category (str): The NIC category (default is 'A').

    Returns:
    float: Calculated NIC tax amount.
    """
    tax_amount = 0

    # Fetch NIC configuration from MongoDB
    nic_config = fetch_nic_config_from_mongodb(nic_category)
    print("nic_config: ",nic_config )

    if not nic_config or 'Rate_Below_LEL' not in nic_config:
        return 'N/A'  # Return N/A if the category doesn't have applicable rates

    LEL = nic_config['LEL']
    PT = nic_config['PT']
    UEL = nic_config['UEL']
    rate_below_lel = nic_config['Rate_Below_LEL']
    rate_between_limits = nic_config['Rate_PT_to_UEL']
    rate_above_upper_limit = nic_config['Rate_Above_UEL']

    if pd.isna(rate_below_lel):
        return 'N/A'  # Return N/A if the category doesn't have applicable rates

    if gross_pay <= PT:
        tax_amount = 0
    elif gross_pay <= UEL:
        rate_between_limits = float(rate_between_limits.strip('%')) / 100
        tax_amount = rate_between_limits * (gross_pay - PT)
    else:
        rate_between_limits = float(rate_between_limits.strip('%')) / 100
        rate_above_upper_limit = float(rate_above_upper_limit.strip('%')) / 100
        tax_amount = (UEL - PT) * rate_between_limits + rate_above_upper_limit * (gross_pay - UEL)

    return round(tax_amount, 2)

# Test cases for calculate_nic_tax_employee_2024
# print("Test Case 1: NIC Category A, Gross Pay below £1,048")
# print("Expected output: 0")
# print("Actual output:", calculate_nic_tax_employee_2024(1000, 'A'), "\n")

# print("Test Case 2: NIC Category A, Gross Pay between £1,048 and £4,189")
# print("Expected output:", 0.08 * (2916.666667 - 1048))
# print("Actual output:", calculate_nic_tax_employee_2024(2916.666667, 'A'), "\n")

# print("Test Case 3: NIC Category A, Gross Pay above £4,189")
# print("Expected output:", (4189 - 1048) * 0.08 + 0.02 * (5000 - 4189))
# print("Actual output:", calculate_nic_tax_employee_2024(5000, 'A'), "\n")

# ---------------------------------------------------------------------------------------------


def fetch_nic_config_employer_from_mongodb(nic_category):
    """
    Fetch NIC configuration for employers from MongoDB for the given NIC category.

    Parameters:
    nic_category (str): The NIC category (e.g., 'A', 'B', etc.)

    Returns:
    dict: A dictionary containing NIC configuration details.
    """
    config = nic_employer_config_collection.find_one({"NIC_Category": nic_category})
    return config

def calculate_nic_tax_employer_2024(gross_pay, nic_category='A'):
    """
    Calculate NIC tax for an employer for 2024 using MongoDB data.

    Parameters:
    gross_pay (float): The gross pay of the employee.
    nic_category (str): The NIC category (default is 'A').

    Returns:
    float: Calculated NIC tax amount.
    """
    tax_amount = 0

    # Fetch NIC configuration from MongoDB
    nic_config = fetch_nic_config_employer_from_mongodb(nic_category)

    if not nic_config:
        return 'N/A'  # Return N/A if the category doesn't have applicable rates

    PT = nic_config['PT']
    ST = nic_config['ST']
    UEL = nic_config['UEL']
    rate_pt_to_st = float(nic_config['Rate_PT_to_ST'].strip('%')) / 100
    rate_st_to_uel = float(nic_config['Rate_ST_to_UEL'].strip('%')) / 100
    rate_above_uel = float(nic_config['Rate_Above_UEL'].strip('%')) / 100

    # Calculate NIC tax based on thresholds
    if gross_pay <= PT:
        tax_amount = 0
    elif gross_pay <= ST:
        tax_amount = rate_pt_to_st * (gross_pay - PT)
    elif gross_pay <= UEL:
        tax_amount = rate_st_to_uel * (gross_pay - ST) + rate_pt_to_st * (ST - PT)
    else:
        tax_amount = rate_above_uel * (gross_pay - UEL) + rate_st_to_uel * (UEL - ST) + rate_pt_to_st * (ST - PT)

    return round(tax_amount, 2)

# # Test cases for calculate_nic_tax_employer_2024
# print("Test Case 1: NIC Category A, Gross Pay below £758")
# print("Expected output: 0")
# print("Actual output:", calculate_nic_tax_employer_2024(700, 'A'), "\n")

# print("Test Case 2: NIC Category A, Gross Pay between £758 and £2,083")
# print("Expected output:", 0.138 * (1000 - 758))
# print("Actual output:", calculate_nic_tax_employer_2024(1000, 'A'), "\n")

# print("Test Case 3: NIC Category A, Gross Pay above £2,083")
# print("Expected output:", 0.138 * (2916.666667 - 2083) + 0.138 * (2083 - 758))
# print("Actual output:", calculate_nic_tax_employer_2024(2916.666667, 'A'), "\n")

# ----------------------------------------------------------------------------------------

def fetch_pension_config_from_mongodb(pension_type):
    """
    Fetch pension contribution configuration from MongoDB for the given type (employee or employer).

    Parameters:
    pension_type (str): The type of pension contribution ('employee' or 'employer').

    Returns:
    dict: A dictionary containing pension contribution details.
    """
    config = pension_config_collection.find_one({"Type": pension_type})
    return config

def calculate_pension_contribution_employee(gross_pay):
    """
    Calculate pension contribution for an employee using MongoDB data.

    Parameters:
    gross_pay (float): The gross pay of the employee.

    Returns:
    float: Calculated pension contribution amount for the employee.
    """
    # Fetch employee pension contribution configuration from MongoDB
    config = fetch_pension_config_from_mongodb('employee')
    # print("config: ",config)

    if not config:
        return 'N/A'  # Return N/A if the configuration doesn't exist

    employee_pension_contribution = config['Contribution_Rate']
    minimum_limit = config['Minimum_Limit']
    maximum_limit = config['Maximum_Limit']

    pension_contribution = 0

    if gross_pay <= minimum_limit:
        pension_contribution = 0
    elif minimum_limit < gross_pay <= maximum_limit or maximum_limit == 0:
        pension_contribution = employee_pension_contribution * (gross_pay - minimum_limit)
    else:
        if maximum_limit != 0:
            pension_contribution = employee_pension_contribution * (maximum_limit - minimum_limit)

    return round(pension_contribution, 2)

def calculate_pension_contribution_employer(gross_pay):
    """
    Calculate pension contribution for an employer using MongoDB data.

    Parameters:
    gross_pay (float): The gross pay of the employee.

    Returns:
    float: Calculated pension contribution amount for the employer.
    """
    # Fetch employer pension contribution configuration from MongoDB
    config = fetch_pension_config_from_mongodb('employer')

    if not config:
        return 'N/A'  # Return N/A if the configuration doesn't exist

    employer_pension_contribution = config['Contribution_Rate']
    minimum_limit = config['Minimum_Limit']
    maximum_limit = config['Maximum_Limit']

    tax_amount = 0

    if gross_pay <= minimum_limit:
        tax_amount = 0
    elif minimum_limit < gross_pay <= maximum_limit or maximum_limit == 0:
        tax_amount = (gross_pay - minimum_limit) * employer_pension_contribution
    else:
        if maximum_limit != 0:
            tax_amount = (maximum_limit - minimum_limit) * employer_pension_contribution

    return round(tax_amount, 2)

# print("Test Case 2: Employee Pension Contribution, Gross Pay within Limits")
# print("Expected output (for example, if limits are 500-1500 and rate is 5%):", 0.05 * (2916.666667 - 0))
# print("Actual output:", calculate_pension_contribution_employee(2916.666667), "\n")

# print("Test Case 3: Employer Pension Contribution, Gross Pay above Maximum Limit")
# print("Expected output (for example, if maximum limit is 1500 and rate is 3%):", 0.03 * (2916.666667 - 0))
# print("Actual output:", calculate_pension_contribution_employer(2916.666667), "\n")


# -----------------------------------------------------------------------------------------

def fetch_student_loan_config_from_mongodb(plan_type):
    """
    Fetch student loan repayment configuration from MongoDB for the given plan type.

    Parameters:
    plan_type (str): The type of student loan plan (e.g., 'Plan 1', 'Plan 2').

    Returns:
    dict: A dictionary containing student loan repayment details.
    """
    config = student_loan_config_collection.find_one({"Plan_Type": plan_type})
    return config

def calculate_student_loan_repayment(gross_pay, student_loan_plan_type):
    """
    Calculate student loan repayment using MongoDB data.

    Parameters:
    gross_pay (float): The gross pay of the employee.
    student_loan_plan_type (str): The type of student loan plan.

    Returns:
    float: Calculated student loan repayment amount.
    """
    # Fetch student loan configuration from MongoDB
    config = fetch_student_loan_config_from_mongodb(student_loan_plan_type)

    if not config:
        return 'N/A'  # Return N/A if the configuration doesn't exist

    threshold = config['Threshold']
    repayment_rate = config['Repayment_Rate']

    repayment_amount = 0

    if gross_pay > threshold:
        repayment_amount = (gross_pay - threshold) * repayment_rate

    return round(repayment_amount, 2)

# Test cases for student loan repayment function
# print("Test Case 1: Student Loan Repayment for Plan 1, Gross Pay below Threshold")
# print("Expected output: 0")
# print("Actual output:", calculate_student_loan_repayment(1800, 'Plan 1'), "\n")

# print("Test Case 2: Student Loan Repayment for Plan 1, Gross Pay above Threshold")
# print("Expected output (for example, if threshold is 1834 and rate is 9%):", 0.09 * (2000 - 1834))
# print("Actual output:", calculate_student_loan_repayment(2000, 'Plan 1'), "\n")

# ----------------------------------------------------------------------------------------

def calculate_take_home(net_pay, pension_contribution_employee):
    """
    Calculate the take-home pay after deducting the employee's pension contribution.

    Parameters:
    net_pay (float): The net pay after taxes and deductions.
    pension_contribution_employee (float): The employee's pension contribution.

    Returns:
    float: The net income after pension contribution deduction.
    """
    print(f"Initial Net Pay: {net_pay}")
    print(f"Employee Pension Contribution: {pension_contribution_employee}")

    net_income_after_pension = net_pay - pension_contribution_employee

    print(f"Net Income After Pension Contribution: {net_income_after_pension}")
    
    return net_income_after_pension

# # Test cases
# print("Test Case 1: Net Pay 3000, Pension Contribution 150")
# print("Expected output: 2850")
# print("Actual output:", calculate_take_home(3000, 150), "\n")

# print("Test Case 2: Net Pay 2500, Pension Contribution 200")
# print("Expected output: 2300")
# print("Actual output:", calculate_take_home(2500, 200), "\n")

# -----------------------------------------------------------------------------------------

def uk_ps_networkdays(start_date, end_date):
    """
    Calculate the number of business days between two dates.

    Parameters:
    start_date (str or datetime): The start date in 'YYYY-MM-DD' format or as a datetime object.
    end_date (str or datetime): The end date in 'YYYY-MM-DD' format or as a datetime object.

    Returns:
    int: The number of business days between the start and end dates.
    """
    
    # Print initial input values
    print(f"Initial Start Date: {start_date}")
    print(f"Initial End Date: {end_date}")
    
    # Convert dates to 'YYYY-MM-DD' format if they are not already
    if isinstance(start_date, datetime):
        start_date = start_date.strftime('%Y-%m-%d')
    if isinstance(end_date, datetime):
        end_date = end_date.strftime('%Y-%m-%d')

    # Print converted dates to ensure they are in the correct format
    print(f"Converted Start Date: {start_date}")
    print(f"Converted End Date: {end_date}")

    # Calculate the number of business days between the two dates
    network_days = np.busday_count(start_date, end_date)

    # Print the calculated number of business days
    print(f"Number of Business Days: {network_days}")
    
    return network_days

# Test cases
# print("Test Case 1: Start Date 2023-09-01, End Date 2023-09-10")
# print("Actual output:", uk_ps_networkdays('2024-09-01', '2024-09-10'), "\n")

# print("Test Case 2: Start Date 2023-12-22, End Date 2024-01-02 (crossing weekends and holidays)")
# print("Actual output:", uk_ps_networkdays('2024-12-22', '2024-01-02'), "\n")

# print("Test Case 3: Start Date 2024-02-01, End Date 2024-02-01 (same day)")
# print("Expected output: 0")
# print("Actual output:", uk_ps_networkdays('2024-02-01', '2024-02-01'), "\n")


# ------------------------------------------------------------------------------------

def uk_ps_rp_sal_deduction(leave_start_date, leave_end_date, salary, period_start_date, period_end_date):
    """
    Calculate salary deduction based on the number of absence days during a pay period.

    Parameters:
    leave_start_date (datetime): The start date of the leave.
    leave_end_date (datetime): The end date of the leave.
    salary (float): The total salary for the pay period.
    period_start_date (datetime): The start date of the pay period.
    period_end_date (datetime): The end date of the pay period.

    Returns:
    float: The calculated salary deduction.
    """
    
    # Calculate total days in the pay period
    total_days = (period_end_date - period_start_date).days + 1
    print(f"Total days in the pay period: {total_days}")

    # Calculate daily salary
    daily_salary = salary / total_days
    print(f"Daily salary: {daily_salary}")

    # Calculate the number of absence days within the pay period
    absence_start = max(leave_start_date, period_start_date)
    absence_end = min(leave_end_date, period_end_date)
    absence_days = (absence_end - absence_start).days + 1
    print(f"Calculated absence days (before correction): {absence_days}")

    # Ensure absence days are not negative
    absence_days = max(absence_days, 0)
    print(f"Corrected absence days: {absence_days}")

    # Calculate the deduction
    deduction = absence_days * daily_salary
    print(f"Calculated deduction: {deduction}")

    return deduction

# # Test cases
# print("Test Case 1: Leave fully within the pay period")
# print("Expected output: (3 days of leave) * daily salary")
# print("Actual output:", uk_ps_rp_sal_deduction(datetime(2024, 2, 5), datetime(2024, 2, 7), 3000, datetime(2024, 2, 1), datetime(2024, 2, 28)), "\n")

# print("Test Case 2: Leave partially overlapping at the start of the pay period")
# print("Expected output: (5 days of leave) * daily salary")
# print("Actual output:", uk_ps_rp_sal_deduction(datetime(2024, 1, 28), datetime(2024, 2, 5), 3000, datetime(2024, 2, 1), datetime(2024, 2, 28)), "\n")

# print("Test Case 3: Leave partially overlapping at the end of the pay period")
# print("Expected output: (2 days of leave) * daily salary")
# print("Actual output:", uk_ps_rp_sal_deduction(datetime(2024, 2, 25), datetime(2024, 3, 1), 3000, datetime(2024, 2, 1), datetime(2024, 2, 28)), "\n")


# -----------------------------------------------------------------------------------------


def UK_PS_SALARY_RETROACTIVE(p_employee_number, p1_payroll_process_date, p2_previous_payroll_process_date, p5_effective_start_payroll_process_date):
    # Establish connection to MongoDB

    l_p1_payroll_process_date = datetime(2023, 6, 15)
    l_p2_previous_payroll_process_date = datetime(2023, 5, 15)
    V_PERIOD = None

    # Fetch v3_sal_last_update_date
    v3_sal_last_update_date = salary_details_collection.find_one(
        {
            "EMPLOYEE_NUMBER": p_employee_number,
            "EFFECTIVE_START_DATE": {"$lte": datetime(2023, 6, 30)},
            "SALARY_CREATION_DATE": {"$lte": l_p1_payroll_process_date}
        },
        sort=[("EFFECTIVE_START_DATE", -1)],
        projection={"SALARY_CREATION_DATE": 1}
    )
    v3_sal_last_update_date = v3_sal_last_update_date['SALARY_CREATION_DATE'] if v3_sal_last_update_date else None

    # Fetch V_ANNUAL_SALARY, V4_EFFECTIVE_START, and V_EFFECTIVE_END
    salary_details = salary_details_collection.find_one(
        {
            "EMPLOYEE_NUMBER": p_employee_number,
            "HOURLY_SALARIED": "Salaried",
            "HR_STATUS": "ACTIVE",
            "SALARY_CREATION_DATE": v3_sal_last_update_date
        },
        sort=[("EFFECTIVE_START_DATE", 1)],
        projection={"ANNUAL_SALARY": 1, "EFFECTIVE_START_DATE": 1, "EFFECTIVE_END_DATE": 1}
    )
    
    if salary_details:
        V_ANNUAL_SALARY = salary_details.get('ANNUAL_SALARY', 0)
        V4_EFFECTIVE_START = salary_details.get('EFFECTIVE_START_DATE', None)
        V_EFFECTIVE_END = salary_details.get('EFFECTIVE_END_DATE', None)
    else:
        V_ANNUAL_SALARY, V4_EFFECTIVE_START, V_EFFECTIVE_END = 0, None, None

    # Fetch v_sal_second_last_update_date
    salary_dates = list(salary_details_collection.find(
        {
            "EMPLOYEE_NUMBER": p_employee_number,
            "EFFECTIVE_START_DATE": {"$lte": datetime(2023, 6, 30)},
            "SALARY_CREATION_DATE": {"$lte": l_p1_payroll_process_date}
        },
        sort=[("EFFECTIVE_START_DATE", -1)],
        projection={"SALARY_CREATION_DATE": 1}
    ))
    v_sal_second_last_update_date = salary_dates[1]['SALARY_CREATION_DATE'] if len(salary_dates) > 1 else None

    # Fetch V_ANNUAL_SALARY_BEFORE_V3
    salary_before_v3 = salary_details_collection.find_one(
        {
            "EMPLOYEE_NUMBER": p_employee_number,
            "HOURLY_SALARIED": "Salaried",
            "HR_STATUS": "ACTIVE",
            "SALARY_CREATION_DATE": v_sal_second_last_update_date
        },
        sort=[("EFFECTIVE_START_DATE", 1)],
        projection={"ANNUAL_SALARY": 1}
    )
    V_ANNUAL_SALARY_BEFORE_V3 = salary_before_v3['ANNUAL_SALARY'] if salary_before_v3 else 0

    # Calculate l_p5_effective_start_payroll_process_date if V4_EFFECTIVE_START is not None
    l_p5_effective_start_payroll_process_date = V4_EFFECTIVE_START.strftime('%Y-%m-%d') if V4_EFFECTIVE_START else None

    # Calculate V_PERIOD
    if V4_EFFECTIVE_START and V4_EFFECTIVE_START > l_p2_previous_payroll_process_date:
        V_PERIOD = 0
    elif V4_EFFECTIVE_START and V4_EFFECTIVE_START < l_p2_previous_payroll_process_date:
        if V4_EFFECTIVE_START < l_p5_effective_start_payroll_process_date:
            V_PERIOD = (l_p2_previous_payroll_process_date.year - V4_EFFECTIVE_START.year) * 12 + l_p2_previous_payroll_process_date.month - V4_EFFECTIVE_START.month + 1
        else:
            V_PERIOD = (l_p2_previous_payroll_process_date.year - V4_EFFECTIVE_START.year) * 12 + l_p2_previous_payroll_process_date.month - V4_EFFECTIVE_START.month

    # Calculate V_RESULT if V_PERIOD is not None
    V_RESULT = V_PERIOD * (V_ANNUAL_SALARY - V_ANNUAL_SALARY_BEFORE_V3) if V_PERIOD is not None else None

    return V_RESULT

# Test cases
# print("Test Case 1: Standard Scenario")
# print("Expected Output: (Depends on your MongoDB data)")
# print("Actual Output:", UK_PS_SALARY_RETROACTIVE("101", datetime(2023, 6, 15), datetime(2023, 5, 15), datetime(2023, 4, 1)))
# print()


# ------------------------------------------------------------------------------------------


def UK_PS_SAP_SMP_FINAL_NEW_2024(p_gross_pay, p_total_weeks_till_now, p_month_weeks):

    # Fetch SMP configuration from MongoDB
    config = smp_config_collection.find_one()

    rate_percentage = config.get('rate_percentage', 0.9)
    fixed_rate = config.get('fixed_rate', 184.03)
    weeks_threshold = config.get('weeks_threshold', 6)
    weeks_in_year = config.get('weeks_in_year', 52)

    v_result = None

    print(f"Rate Percentage: {rate_percentage}")
    print(f"Fixed Rate: {fixed_rate}")
    print(f"Weeks Threshold: {weeks_threshold}")
    print(f"Weeks in Year: {weeks_in_year}")

    if p_total_weeks_till_now == 0:
        if (p_total_weeks_till_now + p_month_weeks) <= weeks_threshold:
            v_result = p_month_weeks * rate_percentage * p_gross_pay * 12 / weeks_in_year
        else:
            if rate_percentage * p_gross_pay * 12 / weeks_in_year >= fixed_rate:
                v_result = fixed_rate * (p_month_weeks + p_total_weeks_till_now - weeks_threshold) + (weeks_threshold - p_total_weeks_till_now) * rate_percentage * p_gross_pay * 12 / weeks_in_year
            else:
                v_result = rate_percentage * p_gross_pay * 12 / weeks_in_year * p_month_weeks
    else:
        if p_total_weeks_till_now <= weeks_threshold:
            if (p_total_weeks_till_now + p_month_weeks) <= weeks_threshold:
                v_result = p_month_weeks * rate_percentage * p_gross_pay * 12 / weeks_in_year
            else:
                if rate_percentage * p_gross_pay * 12 / weeks_in_year >= fixed_rate:
                    v_result = fixed_rate * (p_month_weeks + p_total_weeks_till_now - weeks_threshold) + (weeks_threshold - p_total_weeks_till_now) * rate_percentage * p_gross_pay * 12 / weeks_in_year
                else:
                    v_result = rate_percentage * p_month_weeks * p_gross_pay * 12 / weeks_in_year
        else:
            if rate_percentage * p_gross_pay * 12 / weeks_in_year >= fixed_rate:
                v_result = fixed_rate * p_month_weeks
            else:
                v_result = rate_percentage * p_gross_pay * 12 / weeks_in_year * p_month_weeks

    return v_result

# # Test cases with print statements
# print("Test Case 1: Total weeks till now 0, weeks in the month 4, gross pay 3000")
# print("Expected output: SMP based on calculation logic")
# print("Actual output:", UK_PS_SAP_SMP_FINAL_NEW_2024(3000, 0, 4), "\n")

# print("Test Case 2: Total weeks till now 4, weeks in the month 2, gross pay 2000")
# print("Expected output: SMP based on calculation logic")
# print("Actual output:", UK_PS_SAP_SMP_FINAL_NEW_2024(2000, 4, 2), "\n")

# print("Test Case 3: Total weeks till now 7, weeks in the month 3, gross pay 2500")
# print("Expected output: SMP based on calculation logic")
# print("Actual output:", UK_PS_SAP_SMP_FINAL_NEW_2024(2500, 7, 3), "\n")


# --------------------------------------------------------------------------------------------

from datetime import datetime

def days_between_dates(date1_str, date2_str):
    """
    Calculate the number of days between two string-formatted dates ('%Y-%m-%d %H:%M:%S').
    """
    date1 = datetime.strptime(date1_str, '%Y-%m-%d %H:%M:%S')
    date2 = datetime.strptime(date2_str, '%Y-%m-%d %H:%M:%S')
    return (date2 - date1).days + 1

def UK_PS_SAP_SMP_MONTH_DAYS_NEW(p_start_date, p_end_date, p_sap_start_date, p_previous_month_end, p_sap_end_date):
    """
    Calculate the number of days in a given SAP (Statutory Adoption Pay) period across months using string dates.
    
    All date inputs and outputs will be in string format ('%Y-%m-%d %H:%M:%S').
    """
    
    v_result = None

    print(f"Start Date: {p_start_date}")
    print(f"End Date: {p_end_date}")
    print(f"SAP Start Date: {p_sap_start_date}")
    print(f"Previous Month End: {p_previous_month_end}")
    print(f"SAP End Date: {p_sap_end_date}")

    # Compare the months directly based on strings
    start_month = p_sap_start_date[5:7]
    end_month = p_end_date[5:7]

    # Check if SAP start and end dates are in the same month as the end date
    if start_month == end_month:
        v_result = days_between_dates(p_sap_start_date, p_end_date)
        print(f"Calculation Case 1: SAP start and end date are in the same month. Result: {v_result}")
    
    # Check if start date and SAP end date are in the same month
    elif p_start_date[5:7] == p_sap_end_date[5:7]:
        v_result = days_between_dates(p_start_date, p_sap_end_date)
        print(f"Calculation Case 2: Start date and SAP end date are in the same month. Result: {v_result}")
    
    # Calculate if SAP spans multiple months
    else:
        days_in_full_period = days_between_dates(p_sap_start_date, p_end_date)
        days_in_previous_month = days_between_dates(p_sap_start_date, p_previous_month_end)
        v_result = days_in_full_period - days_in_previous_month
        print(f"Calculation Case 3: SAP spans multiple months. Result: {v_result}")

    return v_result

# # Test cases with print statements
# print("Test Case 1: SAP start and end date are in the same month")
# print("Expected output: Number of days between SAP start and end dates")
# print("Actual output:", UK_PS_SAP_SMP_MONTH_DAYS_NEW(
#     '2024-04-01 00:00:00', '2024-04-30 23:59:59',
#     '2024-02-01 00:00:00', '2024-03-31 00:00:00', '2024-04-17 00:00:00'
# ), "\n")

# print("Test Case 2: Start date and SAP end date are in the same month")
# print("Expected output: Number of days between start date and SAP end date")
# print("Actual output:", UK_PS_SAP_SMP_MONTH_DAYS_NEW(
#     '2024-06-01 00:00:00', '2024-06-30 23:59:59',
#     '2024-05-15 00:00:00', '2024-05-31 00:00:00', '2024-06-01 00:00:00'
# ), "\n")

# print("Test Case 3: SAP spans multiple months")
# print("Expected output: Difference between total days and days in the previous month")
# print("Actual output:", UK_PS_SAP_SMP_MONTH_DAYS_NEW(
#     '2024-05-01 00:00:00', '2024-06-30 23:59:59',
#     '2024-05-15 00:00:00', '2024-05-31 00:00:00', '2024-06-30 00:00:00'
# ), "\n")


# ------------------------------------------------------------------------------------------------

def UK_PS_SAP_SMP_MONTH_WEEKS_NEW(start_date, end_date, sap_start_date, sap_end_date, month_days):
    """
    Calculate the number of weeks of SAP (Statutory Adoption Pay) within a given month period.
    
    All date inputs and outputs will be in string format ('%Y-%m-%d %H:%M:%S').

    Parameters:
    - start_date (str): The start date of the month (in format '%Y-%m-%d %H:%M:%S').
    - end_date (str): The end date of the month (in format '%Y-%m-%d %H:%M:%S').
    - sap_start_date (str): The start date of SAP (in format '%Y-%m-%d %H:%M:%S').
    - sap_end_date (str): The end date of SAP (in format '%Y-%m-%d %H:%M:%S').
    - month_days (int): The number of days in the month.

    Returns:
    - float: The number of SAP weeks within the month.
    """

    # Convert string dates to datetime objects for comparison
    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    end_date_dt = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
    sap_start_date_dt = datetime.strptime(sap_start_date, '%Y-%m-%d %H:%M:%S')
    sap_end_date_dt = datetime.strptime(sap_end_date, '%Y-%m-%d %H:%M:%S')

    print(f"Start Date: {start_date}")
    print(f"End Date: {end_date}")
    print(f"SAP Start Date: {sap_start_date}")
    print(f"SAP End Date: {sap_end_date}")
    print(f"Month Days: {month_days}")

    # Calculate number of weeks if there is an overlap
    if start_date_dt <= sap_end_date_dt and end_date_dt >= sap_start_date_dt:
        result = month_days / 7
        print(f"Calculation Case: Overlapping SAP period. Result: {result}")
    else:
        result = 0
        print(f"Calculation Case: No overlap with SAP period. Result: {result}")
    
    return result

# # Test cases with print statements
# print("Test Case 1: SAP period fully overlaps with the month period")
# print("Expected output: Number of weeks in the month")
# print("Actual output:", UK_PS_SAP_SMP_MONTH_WEEKS_NEW(
#     '2024-06-01 00:00:00', '2024-06-30 23:59:59',
#     '2024-06-01 00:00:00', '2024-06-30 00:00:00', 30
# ), "\n")

# print("Test Case 2: SAP period partially overlaps with the month period")
# print("Expected output: Number of weeks in the overlapping part of the month")
# print("Actual output:", UK_PS_SAP_SMP_MONTH_WEEKS_NEW(
#     '2024-06-01 00:00:00', '2024-06-30 23:59:59',
#     '2024-06-15 00:00:00', '2024-06-30 00:00:00', 15
# ), "\n")

# print("Test Case 3: No overlap between SAP period and the month period")
# print("Expected output: 0")
# print("Actual output:", UK_PS_SAP_SMP_MONTH_WEEKS_NEW(
#     '2024-06-01 00:00:00', '2024-06-30 23:59:59',
#     '2024-07-01 00:00:00', '2024-07-31 00:00:00', 30
# ), "\n")


# ------------------------------------------------------------------------------------------

def UK_PS_SAP_SMP_WEEKS_TLL_NOW(start_date, end_date, sap_start_date, sap_end_date, previous_month_end):
    """
    Calculate the total weeks of SAP (Statutory Adoption Pay) till now within a specified date range.

    Parameters:
    - start_date (datetime or str): The start date of the period.
    - end_date (datetime or str): The end date of the period.
    - sap_start_date (datetime or str): The start date of SAP.
    - sap_end_date (datetime or str): The end date of SAP.
    - previous_month_end (datetime or str): The end date of the previous month.

    Returns:
    - int: The number of SAP weeks till now within the specified period.
    """
    days = 0

    # Convert any string inputs to datetime objects if needed
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
    if isinstance(sap_start_date, str):
        sap_start_date = datetime.strptime(sap_start_date, '%Y-%m-%d %H:%M:%S')
    if isinstance(sap_end_date, str):
        sap_end_date = datetime.strptime(sap_end_date, '%Y-%m-%d %H:%M:%S')
    if isinstance(previous_month_end, str):
        previous_month_end = datetime.strptime(previous_month_end, '%Y-%m-%d %H:%M:%S')

    print(f"Start Date: {start_date}")
    print(f"End Date: {end_date}")
    print(f"SAP Start Date: {sap_start_date}")
    print(f"SAP End Date: {sap_end_date}")
    print(f"Previous Month End: {previous_month_end}")

    if start_date.month == sap_start_date.month:
        days = 0
        print(f"Calculation Case: SAP start month matches start date month. Days: {days}")
    elif start_date.month == sap_end_date.month:
        days = (previous_month_end - sap_start_date).days // 7
        print(f"Calculation Case: SAP end month matches start date month. Days: {days}")
    elif start_date >= sap_start_date and end_date <= sap_end_date:
        days = (previous_month_end - sap_start_date).days // 7
        print(f"Calculation Case: Start and end date within SAP period. Days: {days}")
    else:
        print("Calculation Case: No matching case found.")

    return days

# # Test cases with print statements
# print("Test Case 1: SAP start month matches start date month")
# print("Expected output: 0")
# print("Actual output:", UK_PS_SAP_SMP_WEEKS_TLL_NOW(
#     '2024-04-01 00:00:00', '2024-04-30 23:59:59',
#     '2024-02-01 01:00:00', '2024-06-30 01:00:00', '2024-03-31 00:00:00'
# ), "\n")

# print("Test Case 2: SAP end month matches start date month")
# print("Expected output: Number of weeks till the end of the previous month")
# print("Actual output:", UK_PS_SAP_SMP_WEEKS_TLL_NOW(
#     '2024-02-01 00:00:00', '2024-02-28 23:59:59',  # Corrected February date
#     '2024-02-01 01:00:00', '2024-06-30 01:00:00', '2024-02-28 00:00:00'
# ), "\n")

# print("Test Case 3: Start and end date within SAP period")
# print("Expected output: Number of weeks till the end of the previous month")
# print("Actual output:", UK_PS_SAP_SMP_WEEKS_TLL_NOW(
#     '2024-03-01 00:00:00', '2024-03-30 23:59:59',
#     '2024-02-01 01:00:00', '2024-06-30 01:00:00', '2024-02-28 00:00:00'  # Corrected previous month end
# ), "\n")


# ---------------------------------------------------------------------------------------------------------


def UK_PS_SPP_FINAL_NEW_2024(gross_pay, month_weeks):
    """
    Calculate the Statutory Paternity Pay (SPP) for a given period.

    Parameters:
    - gross_pay (float): The gross pay of the employee.
    - month_weeks (float): The number of weeks in the month for which SPP is being calculated.

    Returns:
    - float: The calculated SPP for the period.
    """
    print(f"Calculating SPP for Gross Pay: {gross_pay}, Month Weeks: {month_weeks}")

    if 0.9 * gross_pay * 12 / 52 > 172.48:
        result = month_weeks * 172.48
        print(f"SPP capped at the statutory limit. Result: {result}")
    else:
        result = 0.9 * gross_pay * 12 / 52 * month_weeks
        print(f"SPP calculated as 90% of gross pay. Result: {result}")

    return result

# # Test cases with print statements
# print("Test Case 1: Gross pay above the threshold for maximum SPP")
# print("Expected output: SPP capped at 172.48 per week multiplied by the number of weeks")
# print("Actual output:", UK_PS_SPP_FINAL_NEW_2024(5000, 4), "\n")

# print("Test Case 2: Gross pay below the threshold for maximum SPP")
# print("Expected output: SPP calculated as 90% of gross pay per week multiplied by the number of weeks")
# print("Actual output:", UK_PS_SPP_FINAL_NEW_2024(1000, 4), "\n")

# print("Test Case 3: Gross pay exactly at the threshold for maximum SPP")
# print("Expected output: SPP calculated as 90% of gross pay per week multiplied by the number of weeks")
# print("Actual output:", UK_PS_SPP_FINAL_NEW_2024(2000, 4), "\n")

# -----------------------------------------------------------------------------------------------------------


def UK_PS_SPP_MONTH_DAYS(start_date, end_date, spp_start_date, spp_end_date, previous_month_end, total_weeks):
    """
    Calculate the number of days for which SPP is applicable in a given month.

    Parameters:
    - start_date (datetime): Start date of the period.
    - end_date (datetime): End date of the period.
    - spp_start_date (datetime): SPP start date.
    - spp_end_date (datetime): SPP end date.
    - previous_month_end (datetime): End date of the previous month.
    - total_weeks (int): Total weeks to calculate SPP for.

    Returns:
    - int: Number of days for which SPP is applicable.
    """
    
    print(f"Calculating SPP Month Days for Start Date: {start_date}, End Date: {end_date}, SPP Start Date: {spp_start_date}, SPP End Date: {spp_end_date}, Previous Month End: {previous_month_end}, Total Weeks: {total_weeks}")
    
    if spp_start_date.month == spp_end_date.month:
        result = 7 * total_weeks
        print(f"SPP start and end date in the same month. Result: {result}")
    elif spp_start_date.month == start_date.month:
        result = (end_date - spp_start_date).days + 1
        print(f"SPP start date in the same month as the start date. Days between SPP start and end date: {result}")
    elif spp_start_date.month == spp_end_date.month:
        result = (spp_end_date - spp_start_date).days - (previous_month_end - spp_start_date).days + (previous_month_end - spp_start_date).days - 7 * ((previous_month_end - spp_start_date).days // 7)
        print(f"SPP start and end date in the same month with some adjustments. Result: {result}")
    else:
        result = (end_date - spp_start_date).days - (previous_month_end - spp_start_date).days + (previous_month_end - spp_start_date).days - 7 * ((previous_month_end - spp_start_date).days // 7)
        print(f"General case calculation for SPP days. Result: {result}")
    
    return result

# # Test cases with print statements
# print("Test Case 1: SPP start and end date in the same month")
# print("Expected output: 7 * total_weeks")
# print("Actual output:", UK_PS_SPP_MONTH_DAYS(datetime(2024, 5, 1), datetime(2024, 5, 31), datetime(2024, 5, 5), datetime(2024, 5, 25), datetime(2024, 4, 30), 3), "\n")

# print("Test Case 2: SPP start date in the same month as the start date")
# print("Expected output: Days between end_date and spp_start_date")
# print("Actual output:", UK_PS_SPP_MONTH_DAYS(datetime(2024, 5, 1), datetime(2024, 5, 31), datetime(2024, 5, 15), datetime(2024, 6, 10), datetime(2024, 4, 30), 3), "\n")

# print("Test Case 3: General case calculation")
# print("Expected output: Complex calculation for SPP days")
# print("Actual output:", UK_PS_SPP_MONTH_DAYS(datetime(2024, 5, 1), datetime(2024, 5, 31), datetime(2024, 4, 15), datetime(2024, 6, 10), datetime(2024, 4, 30), 3), "\n")


# -----------------------------------------------------------------------------------------------------------------


def parse_date(date_str):
    """
    Helper function to parse a date string into a datetime object.
    Supports multiple formats and returns None if parsing fails.
    """
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        try:
            return datetime.strptime(date_str, '%d-%b-%y %I.%M.%S.%f000000 %p')
        except ValueError:
            print(f"Failed to parse date: {date_str}")
            return None

def UK_PS_SPP_MONTH_DAYS_NEW(p_start_date, p_end_date, p_spp_start_date, p_previous_month_end, p_spp_end_date):
    """
    Calculate the number of days for which SPP is applicable in a given period.

    Parameters:
    - p_start_date (str/datetime): Start date of the period.
    - p_end_date (str/datetime): End date of the period.
    - p_spp_start_date (str/datetime): SPP start date.
    - p_previous_month_end (str/datetime): End date of the previous month.
    - p_spp_end_date (str/datetime): SPP end date.

    Returns:
    - int: Number of days for which SPP is applicable.
    """
    
    # Convert all input dates from strings to datetime objects
    p_start_date = parse_date(p_start_date)
    p_end_date = parse_date(p_end_date)
    p_spp_start_date = parse_date(p_spp_start_date)
    p_previous_month_end = parse_date(p_previous_month_end)
    p_spp_end_date = parse_date(p_spp_end_date)

    # Return early if any date parsing failed
    if any(d is None for d in [p_start_date, p_end_date, p_spp_start_date, p_previous_month_end, p_spp_end_date]):
        return 0

    print(f"Start Date: {p_start_date}, End Date: {p_end_date}, SPP Start Date: {p_spp_start_date}, Previous Month End: {p_previous_month_end}, SPP End Date: {p_spp_end_date}")

    # Calculate the number of days based on conditions
    if p_spp_start_date.month == p_spp_end_date.month:
        v_result = (p_spp_end_date - p_spp_start_date).days + 1
        print(f"SPP start and end date are in the same month. Result: {v_result}")
    elif p_spp_start_date.month == p_start_date.month:
        v_result = (p_end_date - p_spp_start_date).days + 1
        print(f"SPP start date is in the same month as the start date. Result: {v_result}")
    elif p_start_date.month == p_spp_end_date.month:
        v_result = (p_spp_end_date - p_start_date).days + 1
        print(f"SPP end date is in the same month as the start date. Result: {v_result}")
    else:
        v_result = (p_end_date - p_start_date).days + 1
        print(f"General case calculation. Result: {v_result}")

    return v_result

# # Test cases with print statements
# print("Test Case 1: SPP start and end date are in the same month")
# print("Expected output: Number of days between SPP start and end date")
# print("Actual output:", UK_PS_SPP_MONTH_DAYS_NEW('2024-05-01', '2024-05-31', '2024-05-05', '2024-04-30', '2024-05-25'), "\n")

# print("Test Case 2: SPP start date in the same month as the start date")
# print("Expected output: Number of days between end date and SPP start date")
# print("Actual output:", UK_PS_SPP_MONTH_DAYS_NEW('2024-05-01', '2024-05-31', '2024-05-15', '2024-04-30', '2024-06-10'), "\n")

# print("Test Case 3: SPP end date in the same month as the start date")
# print("Expected output: Number of days between SPP end date and start date")
# print("Actual output:", UK_PS_SPP_MONTH_DAYS_NEW('2024-05-01', '2024-05-31', '2024-04-15', '2024-04-30', '2024-05-10'), "\n")

# print("Test Case 4: General case calculation")
# print("Expected output: Number of days between start date and end date")
# print("Actual output:", UK_PS_SPP_MONTH_DAYS_NEW('2024-05-01', '2024-05-31', '2024-04-15', '2024-04-30', '2024-06-10'), "\n")


def UK_PS_SPP_MONTH_WEEKS_NEW(start_date, end_date, spp_start_date, spp_end_date, month_days):
    """
    Calculate the number of weeks for which SPP is applicable in a given period.

    Parameters:
    - start_date (str/datetime): Start date of the period.
    - end_date (str/datetime): End date of the period.
    - spp_start_date (str/datetime): SPP start date.
    - spp_end_date (str/datetime): SPP end date.
    - month_days (int): Number of days in the month.

    Returns:
    - float: Number of weeks for which SPP is applicable.
    """
    
    # Ensure all dates are datetime objects
    start_date = parse_date(start_date)
    end_date = parse_date(end_date)
    spp_start_date = parse_date(spp_start_date)
    spp_end_date = parse_date(spp_end_date)

    # Check if parsing was successful for all dates
    if None in [start_date, end_date, spp_start_date, spp_end_date]:
        print("One or more dates could not be parsed.")
        return 0

    print(f"Start Date: {start_date}, End Date: {end_date}, SPP Start Date: {spp_start_date}, SPP End Date: {spp_end_date}")

    # Perform the comparison
    if start_date <= spp_end_date and end_date >= spp_start_date:
        result = month_days / 7
        print(f"SPP is applicable for {result:.2f} weeks.")
    else:
        result = 0
        print("SPP is not applicable in the given period.")

    return result

# # Test cases with print statements
# print("Test Case 1: SPP applicable period")
# print("Expected output: Number of weeks based on month_days")
# print("Actual output:", UK_PS_SPP_MONTH_WEEKS_NEW('2024-05-01', '2024-05-31', '2024-05-10', '2024-05-25', 30), "\n")

# print("Test Case 2: SPP not applicable period")
# print("Expected output: 0")
# print("Actual output:", UK_PS_SPP_MONTH_WEEKS_NEW('2024-05-01', '2024-05-31', '2024-06-01', '2024-06-15', 30), "\n")

# print("Test Case 3: SPP start date before and end date after the period")
# print("Expected output: Number of weeks based on month_days")
# print("Actual output:", UK_PS_SPP_MONTH_WEEKS_NEW('2024-05-01', '2024-05-31', '2024-04-25', '2024-06-05', 30), "\n")



def UK_PS_SPP_WEEKS_TLL_NOW_NEW(start_date, end_date, spp_start_date_str, spp_end_date_str, previous_month_end_str):
    """
    Calculate the number of weeks till now for SPP.

    Parameters:
    - start_date (str/datetime): Start date of the period.
    - end_date (str/datetime): End date of the period.
    - spp_start_date_str (str): SPP start date as a string.
    - spp_end_date_str (str): SPP end date as a string.
    - previous_month_end_str (str): Previous month's end date as a string.

    Returns:
    - int: Number of weeks till now for SPP.
    """
    
    # Convert string dates to datetime objects if they are strings using the new parsing function
    start_date = parse_date(start_date) if isinstance(start_date, str) else start_date
    end_date = parse_date(end_date) if isinstance(end_date, str) else end_date
    spp_start_date = parse_date(spp_start_date_str) if isinstance(spp_start_date_str, str) else spp_start_date_str
    spp_end_date = parse_date(spp_end_date_str) if isinstance(spp_end_date_str, str) else spp_end_date_str
    previous_month_end = parse_date(previous_month_end_str) if isinstance(previous_month_end_str, str) else previous_month_end_str

    # Return early if any date failed to parse
    if not all([start_date, end_date, spp_start_date, spp_end_date, previous_month_end]):
        print("One or more dates could not be parsed.")
        return 0

    print(f"Start Date: {start_date}, End Date: {end_date}, SPP Start Date: {spp_start_date}, SPP End Date: {spp_end_date}, Previous Month End: {previous_month_end}")

    # Calculate the number of weeks based on conditions
    if start_date.month == spp_start_date.month:
        result = 0
    elif start_date.month == spp_end_date.month:
        result = (previous_month_end - spp_start_date + timedelta(days=1)).days // 7
    elif start_date >= spp_start_date and end_date <= spp_end_date:
        result = (previous_month_end - spp_start_date + timedelta(days=1)).days // 7
    else:
        result = 0

    print(f"Calculated weeks till now: {result}")
    return result

# # Test cases
# print("Test Case 1: SPP starts in the same month as the period start")
# print("Expected output: 0")
# print("Actual output:", UK_PS_SPP_WEEKS_TLL_NOW_NEW('2024-05-01', '2024-05-31', '2024-05-10', '2024-06-15', '2024-05-31'), "\n")

# print("Test Case 2: SPP starts before and ends within the period")
# print("Expected output: Weeks count from start till previous month end")
# print("Actual output:", UK_PS_SPP_WEEKS_TLL_NOW_NEW('2024-05-01', '2024-05-31', '2024-04-15', '2024-06-15', '2024-05-31'), "\n")

# print("Test Case 3: SPP starts before the period start and ends after the period end")
# print("Expected output: Weeks count from start till previous month end")
# print("Actual output:", UK_PS_SPP_WEEKS_TLL_NOW_NEW('2024-05-01', '2024-05-31', '2024-04-01', '2024-07-01', '2024-05-31'), "\n")

# print("Test Case 4: Invalid date format")
# print("Expected output: Error message and 0")
# print("Actual output:", UK_PS_SPP_WEEKS_TLL_NOW_NEW('invalid-date', '2024-05-31', '2024-05-10', '2024-06-15', '2024-05-31'), "\n")


# ---------------------------------------------------------------------------------------

def uk_ps_ssp_final_2024(p_SSP_start_date, p_End_date, p_SSP_end_date, p_Start_date):
    # Helper function to parse date strings to datetime objects
    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, '%d-%b-%y %I.%M.%S.%f %p')
        except ValueError:
            # Handle cases where microseconds are not provided
            return datetime.strptime(date_str, '%d-%b-%y %I.%M.%S %p')

    # Convert all date inputs to datetime objects
    p_SSP_start_date = parse_date(p_SSP_start_date)
    p_End_date = parse_date(p_End_date)
    p_SSP_end_date = parse_date(p_SSP_end_date)
    p_Start_date = parse_date(p_Start_date)

    # Additional working days are added to the start date
    p_SSP_new_start_date = uk_ps_add_working_days(p_SSP_start_date, 3)
    if p_SSP_end_date is None or p_SSP_new_start_date is None:
        return 0  # Early return if any date is not defined

    # Check conditions
    if p_SSP_end_date < p_Start_date or p_SSP_new_start_date > p_End_date:
        v_SSP_month = 0
    elif p_SSP_new_start_date.year == p_SSP_end_date.year and p_SSP_new_start_date.month == p_SSP_end_date.month:
        v_SSP_month = uk_ps_networkdays(p_SSP_new_start_date, p_SSP_end_date) / 5 * 116.75
    else:
        if p_SSP_new_start_date.year == p_End_date.year and p_SSP_new_start_date.month == p_End_date.month:
            v_SSP_month = uk_ps_networkdays(p_SSP_new_start_date, p_End_date) / 5 * 116.75
        elif p_SSP_end_date.year == p_End_date.year and p_SSP_end_date.month == p_End_date.month:
            v_SSP_month = uk_ps_networkdays(p_Start_date, p_SSP_end_date) / 5 * 116.75
        else:
            v_SSP_month = uk_ps_networkdays(p_Start_date, p_End_date) / 5 * 116.75

    return v_SSP_month


# # Test cases for uk_ps_ssp_final_2024 function
# print("Test Case 1: SSP period within a single month")
# print("Expected output: Calculated SSP for the number of network days within the same month")
# print("Actual output:", uk_ps_ssp_final_2024('01-Jan-24 12.00.00.000000 AM', '31-Jan-24 12.00.00.000000 AM', '20-Jan-24 12.00.00.000000 AM', '01-Jan-24 12.00.00.000000 AM'), "\n")

# print("Test Case 2: SSP period spans two months")
# print("Expected output: Calculated SSP for part of the period")
# print("Actual output:", uk_ps_ssp_final_2024('20-Dec-23 12.00.00.000000 AM', '31-Jan-24 12.00.00.000000 AM', '10-Jan-24 12.00.00.000000 AM', '01-Dec-23 12.00.00.000000 AM'), "\n")

# print("Test Case 3: No SSP due to end date before SSP starts")
# print("Expected output: 0 (No SSP due)")
# print("Actual output:", uk_ps_ssp_final_2024('01-Feb-24 12.00.00.000000 AM', '31-Jan-24 12.00.00.000000 AM', '10-Feb-24 12.00.00.000000 AM', '01-Jan-24 12.00.00.000000 AM'), "\n")

# print("Test Case 4: SSP start date is after the end date")
# print("Expected output: 0 (No SSP due)")
# print("Actual output:", uk_ps_ssp_final_2024('01-Jan-24 12.00.00.000000 AM', '15-Jan-24 12.00.00.000000 AM', '30-Dec-23 12.00.00.000000 AM', '01-Jan-24 12.00.00.000000 AM'), "\n")

# ----------------------------------------------------------------------------------------


def uk_ps_unpaid_streak(p_LEAVE_START_DATE_TIME, p_payroll_process_start_date, p_payroll_process_end_date, p_LEAVE_END_DATE_TIME):
    # Convert dates to datetime objects if they are not already
    if not isinstance(p_LEAVE_START_DATE_TIME, datetime):
        p_LEAVE_START_DATE_TIME = datetime.combine(p_LEAVE_START_DATE_TIME, datetime.min.time())
    if not isinstance(p_payroll_process_start_date, datetime):
        p_payroll_process_start_date = datetime.combine(p_payroll_process_start_date, datetime.min.time())
    if not isinstance(p_payroll_process_end_date, datetime):
        p_payroll_process_end_date = datetime.combine(p_payroll_process_end_date, datetime.max.time())
    if not isinstance(p_LEAVE_END_DATE_TIME, datetime):
        p_LEAVE_END_DATE_TIME = datetime.combine(p_LEAVE_END_DATE_TIME, datetime.max.time())

    v_sap = 0
    if p_LEAVE_START_DATE_TIME >= p_payroll_process_start_date and p_LEAVE_END_DATE_TIME <= p_payroll_process_end_date:
        v_sap = (p_LEAVE_END_DATE_TIME - p_LEAVE_START_DATE_TIME).days + 1
    elif p_LEAVE_START_DATE_TIME >= p_payroll_process_start_date and p_LEAVE_START_DATE_TIME <= p_payroll_process_end_date:
        v_sap = (p_payroll_process_end_date - p_LEAVE_START_DATE_TIME).days + 1
    elif p_LEAVE_END_DATE_TIME >= p_payroll_process_start_date and p_LEAVE_END_DATE_TIME <= p_payroll_process_end_date:
        v_sap = (p_LEAVE_END_DATE_TIME - p_payroll_process_start_date).days + 1
    return v_sap

# Test cases for uk_ps_unpaid_streak function
# # Test Case 1: Leave entirely within the payroll period
# print("Test Case 1: Leave entirely within the payroll period")
# print("Expected output: 5 days")
# print("Actual output:", uk_ps_unpaid_streak(datetime(2024, 1, 10), datetime(2024, 1, 1), datetime(2024, 1, 31), datetime(2024, 1, 14)), "\n")

# # Test Case 2: Leave starts within payroll period and ends after it
# print("Test Case 2: Leave starts within payroll period and ends after it")
# print("Expected output: 10 days")
# print("Actual output:", uk_ps_unpaid_streak(datetime(2024, 1, 25), datetime(2024, 1, 1), datetime(2024, 1, 31), datetime(2024, 2, 5)), "\n")

# # Test Case 3: Leave starts before payroll period and ends within it
# print("Test Case 3: Leave starts before payroll period and ends within it")
# print("Expected output: 7 days")
# print("Actual output:", uk_ps_unpaid_streak(datetime(2023, 12, 25), datetime(2024, 1, 1), datetime(2024, 1, 31), datetime(2024, 1, 7)), "\n")


# -------------------------------------------------------------------------------------------------------

def uk_ps_ytd_maternity(v_emp_num, v_start_date, v_end_date, v_maternity_gross, v_client_id):
    """
    Calculate Year-to-Date maternity benefits using MongoDB for data fetching.
    """
    
    # Ensure dates are datetime objects
    if not isinstance(v_start_date, datetime) or not isinstance(v_end_date, datetime):
        print("Invalid date input. Dates must be datetime objects.")
        return 0.0
    
    v_smp_final_value = 0
    v_previous_month_end = v_start_date - timedelta(days=1)
    
    # Fetch maternity leave data from MongoDB
    maternity_leave_data = list(absence_details_collection.find({
        'EMPLOYEE_ID': v_emp_num,
        'LEAVE_TYPE': 'Maternity Leave',
        'CLIENT_ID': v_client_id,
        'LEAVE_START_DATE_TIME': {'$lte': v_end_date},
        'LEAVE_END_DATE_TIME': {'$gte': v_start_date}
    }, {
        'LEAVE_START_DATE_TIME': 1,
        'LEAVE_END_DATE_TIME': 1
    }))

    if not maternity_leave_data:
        print("No maternity leave records found for the provided parameters.")
    
    # Iterate over fetched maternity leave data
    for j in maternity_leave_data:
        v_smp_start_date = j['LEAVE_START_DATE_TIME']
        v_smp_end_date = j.get('LEAVE_END_DATE_TIME', v_end_date)

        # Call functions for SMP calculations (assuming these functions are defined)
        v_uk_smp_weeks_tll_now = UK_PS_SAP_SMP_WEEKS_TLL_NOW(v_start_date, v_end_date, v_smp_start_date, v_smp_end_date, v_previous_month_end)
        v_uk_smp_month_days = UK_PS_SAP_SMP_MONTH_DAYS_NEW(v_start_date, v_end_date, v_smp_start_date, v_previous_month_end, v_smp_end_date)
        v_uk_smp_month_weeks = UK_PS_SAP_SMP_MONTH_WEEKS_NEW(v_start_date, v_end_date, v_smp_start_date, v_smp_end_date, v_uk_smp_month_days)

        # Calculate final SMP value
        v_smp_final_value += UK_PS_SAP_SMP_FINAL_NEW_2024(v_maternity_gross, v_uk_smp_weeks_tll_now, v_uk_smp_month_weeks)

    return v_smp_final_value

# # Test cases for uk_ps_ytd_maternity function
# print("Test Case 1: Valid employee number and date range")
# print("Expected output: A float value representing the total YTD maternity benefits")
# print("Actual output:", uk_ps_ytd_maternity('EMP123', datetime(2024, 1, 1), datetime(2024, 12, 31), 5000, 'client_001'), "\n")

# print("Test Case 2: Employee number with no maternity leave records")
# print("Expected output: 0.0")
# print("Actual output:", uk_ps_ytd_maternity('NON_EXISTENT_EMP', datetime(2024, 1, 1), datetime(2024, 12, 31), 5000, 'client_001'), "\n")

# print("Test Case 3: Invalid date range")
# print("Expected output: Error or 0.0")
# print("Actual output:", uk_ps_ytd_maternity('EMP123', 'invalid_date', datetime(2024, 12, 31), 5000, 'client_001'), "\n")


# -------------------------------------------------------------------------------------------------------

def uk_ps_ytd_paternity(v_emp_num, v_start_date, v_end_date, v_paternity_gross, v_client_id):
    """
    Calculate Year-to-Date paternity benefits using MongoDB for data fetching.

    Parameters:
    - v_emp_num: Employee number
    - v_start_date: Start date for YTD calculation
    - v_end_date: End date for YTD calculation
    - v_paternity_gross: Gross paternity pay
    - v_client_id: Client identifier

    Returns:
    - V_SPP_FINAL_VALUE: Total YTD paternity benefits
    """
    # Ensure dates are datetime objects
    if not isinstance(v_start_date, datetime) or not isinstance(v_end_date, datetime):
        print("Invalid date input. Dates must be datetime objects.")
        return 0.0

    V_SPP_FINAL_VALUE = 0
    v_previous_month_end = v_start_date - timedelta(days=1)

    # Fetch paternity leave data from MongoDB
    paternity_leave_data = list(absence_details_collection.find({
        'EMPLOYEE_ID': v_emp_num,
        'LEAVE_TYPE': 'GB Paternity Leave',
        'CLIENT_ID': v_client_id,
        'LEAVE_START_DATE_TIME': {'$lte': v_end_date},
        'LEAVE_END_DATE_TIME': {'$gte': v_start_date}
    }, {
        'LEAVE_START_DATE_TIME': 1,
        'LEAVE_END_DATE_TIME': 1
    }))

    # Iterate over fetched paternity leave data
    for leave_instance in paternity_leave_data:
        v_spp_start_date = leave_instance['LEAVE_START_DATE_TIME']
        v_spp_end_date = leave_instance.get('LEAVE_END_DATE_TIME', v_end_date)

        # Calculate SPP weeks till now, month days, and month weeks
        V_UK_SPP_WEEKS_TLL_NOW = UK_PS_SPP_WEEKS_TLL_NOW_NEW(v_start_date, v_end_date, v_spp_start_date, v_spp_end_date, v_previous_month_end)
        V_UK_PS_SPP_MONTH_DAYS = UK_PS_SPP_MONTH_DAYS_NEW(v_start_date, v_end_date, v_spp_start_date, v_previous_month_end, v_spp_end_date)
        V_UK_SPP_MONTH_WEEKS = UK_PS_SPP_MONTH_WEEKS_NEW(v_start_date, v_end_date, v_spp_start_date, v_spp_end_date, V_UK_PS_SPP_MONTH_DAYS)

        # Calculate final SPP value
        V_SPP_FINAL_VALUE += UK_PS_SPP_FINAL_NEW_2024(v_paternity_gross, V_UK_SPP_MONTH_WEEKS)

    return V_SPP_FINAL_VALUE

# # Test cases for uk_ps_ytd_paternity function
# print("Test Case 1: Valid employee number and date range")
# print("Expected output: A float value representing the total YTD paternity benefits")
# print("Actual output:", uk_ps_ytd_paternity('EMP123', datetime(2024, 1, 1), datetime(2024, 12, 31), 5000, 'client_001'), "\n")

# print("Test Case 2: Employee number with no paternity leave records")
# print("Expected output: 0.0")
# print("Actual output:", uk_ps_ytd_paternity('NON_EXISTENT_EMP', datetime(2024, 1, 1), datetime(2024, 12, 31), 5000, 'client_001'), "\n")

# print("Test Case 3: Invalid date range")
# print("Expected output: Error or 0.0")
# print("Actual output:", uk_ps_ytd_paternity('EMP123', 'invalid_date', datetime(2024, 12, 31), 5000, 'client_001'), "\n")

# ------------------------------------------------------------------------------------------


def fetch_annual_salary_1(emp_num, start_date, end_date, client_id):
    """
    Fetches the annual salary for a given employee within a specific date range from MongoDB.
    """

    # Attempt to convert input dates to datetime objects if they are strings
    try:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError as e:
        print(f"Error converting dates: {e}")
        return 0, None, None

    # Debugging: Print the query criteria
    print("Querying MongoDB with:")
    print(f"Employee Number: {emp_num}, Start Date: {start_date}, End Date: {end_date}, Client ID: {client_id}")

    # Query MongoDB to fetch salary details
    salary_data = salary_details_collection.find_one({
        'EMPLOYEE_NUMBER': emp_num,
        'HOURLY_SALARIED': 'Salaried',
        'HR_STATUS': 'ACTIVE',
        'EFFECTIVE_START_DATE': {'$lte': end_date},
        'EFFECTIVE_END_DATE': {'$gte': start_date},
        'CLIENT_ID': client_id
    }, sort=[('EFFECTIVE_START_DATE', -1)])

    # Debugging: Print the fetched data
    print("Fetched salary data:", salary_data)

    if salary_data:
        annual_salary = float(salary_data.get('ANNUAL_SALARY', 0))
        effective_start_date = salary_data.get('EFFECTIVE_START_DATE')
        effective_end_date = salary_data.get('EFFECTIVE_END_DATE')
        return annual_salary, effective_start_date, effective_end_date
    else:
        return 0, None, None

# # Test cases for fetch_annual_salary_1 function
# print("Test Case 1: Valid employee number and date range")
# print("Expected output: (annual_salary, effective_start_date, effective_end_date)")
# print("Actual output:", fetch_annual_salary_1('EMP123', '2024-01-01', '2024-12-31', 'client_001'), "\n")

# print("Test Case 2: Employee number with no active salary records")
# print("Expected output: (0, None, None)")
# print("Actual output:", fetch_annual_salary_1('NON_EXISTENT_EMP', '2024-01-01', '2024-12-31', 'client_001'), "\n")

# print("Test Case 3: Invalid date range")
# print("Expected output: (0, None, None)")
# print("Actual output:", fetch_annual_salary_1('EMP123', 'invalid_date', '2024-12-31', 'client_001'), "\n")


# -----------------------------------------------------------------------------------------


def uk_ps_ytd_salary_2(v_emp_num, p_ytd_start_date, p_ytd_end_date, v_client_id):
    """
    Calculate the year-to-date (YTD) salary for an employee based on monthly salary data from MongoDB.

    Parameters:
    v_emp_num (str): Employee number.
    p_ytd_start_date (str): Start date for the YTD calculation in 'YYYY-MM-DD' format.
    p_ytd_end_date (str): End date for the YTD calculation in 'YYYY-MM-DD' format.
    v_client_id (str): Client identifier.

    Returns:
    float: The total YTD salary.
    """
    v_total_ytd_salary = 0
    v_ytd_start_date = datetime.strptime(p_ytd_start_date, '%Y-%m-%d')
    v_ytd_end_date = datetime.strptime(p_ytd_end_date, '%Y-%m-%d')
    v_current_date = v_ytd_start_date.replace(day=1)

    while v_current_date <= v_ytd_end_date.replace(day=1):
        v_start_date = v_current_date.replace(day=1)
        v_end_date = (v_current_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        # Fetch annual salary using MongoDB function
        v_annual_salary, v_effective_start_date, v_effective_end_date = fetch_annual_salary_1(v_emp_num, v_start_date, v_end_date, v_client_id)

        # Calculate monthly salary and add to YTD total if effective dates are valid
        if v_effective_start_date is not None and v_effective_end_date is not None:
            v_monthly_salary = v_annual_salary / 12
            v_total_ytd_salary += v_monthly_salary

        # Move to the next month
        v_current_date = v_current_date.replace(day=1) + timedelta(days=32)

    return v_total_ytd_salary

# # Test cases for uk_ps_ytd_salary_2 function
# print("Test Case 1: Valid employee number and date range")
# print("Expected output: Calculated YTD salary based on data in MongoDB")
# print("Actual output:", uk_ps_ytd_salary_2('EMP123', '2024-01-01', '2024-12-31', 'client_001'), "\n")

# print("Test Case 2: Employee with no active salary records")
# print("Expected output: 0")
# print("Actual output:", uk_ps_ytd_salary_2('NON_EXISTENT_EMP', '2024-01-01', '2024-12-31', 'client_001'), "\n")

# print("Test Case 3: Invalid date range")
# print("Expected output: 0")
# print("Actual output:", uk_ps_ytd_salary_2('EMP123', 'invalid_date', '2024-12-31', 'client_001'), "\n")


# --------------------------------------------------------------------------------------------

def uk_ps_ytd_salary_deduction(emp_num, start_date, end_date, absence_type, client_id):
    total_deduction = 0

    # Convert string inputs to datetime objects if needed
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

    # Fetch absence records from MongoDB
    absence_records = absence_details_collection.find({
        "EMPLOYEE_ID": emp_num,
        "LEAVE_TYPE": absence_type,
        "LEAVE_START_DATE_TIME": {"$lte": end_date.strftime('%Y-%m-%d %H:%M:%S')},
        "LEAVE_END_DATE_TIME": {"$gte": start_date.strftime('%Y-%m-%d %H:%M:%S')},
        "CLIENT_ID": client_id
    }, {"LEAVE_START_DATE_TIME": 1, "LEAVE_END_DATE_TIME": 1})

    for abs_rec in absence_records:
        abs_start = max(datetime.strptime(abs_rec['LEAVE_START_DATE_TIME'], '%Y-%m-%d %H:%M:%S'), start_date)
        # print("abs_start: ", abs_start)
        # print()
        abs_end = min(datetime.strptime(abs_rec['LEAVE_END_DATE_TIME'], '%Y-%m-%d %H:%M:%S'), end_date)
        # print("abs_stabs_endart: ", abs_end)
        # print()
        # Fetch salary records from MongoDB
        salary_records = salary_details_collection.find({
            "EMPLOYEE_NUMBER": emp_num,
            "EFFECTIVE_START_DATE": {"$lte": abs_end.strftime('%Y-%m-%d %H:%M:%S')},
            "$or": [{"EFFECTIVE_END_DATE": {"$exists": False}}, {"EFFECTIVE_END_DATE": {"$gte": abs_start.strftime('%Y-%m-%d %H:%M:%S')}}],
            "CLIENT_ID": client_id
        }, {"ANNUAL_SALARY": 1, "EFFECTIVE_START_DATE": 1, "EFFECTIVE_END_DATE": 1}).sort("EFFECTIVE_START_DATE", 1)

        for sal_rec in salary_records:
            salary = sal_rec['ANNUAL_SALARY']
            salary_change = max(datetime.strptime(sal_rec['EFFECTIVE_START_DATE'], '%Y-%m-%d %H:%M:%S'), abs_start)
            processed = False

            while salary_change <= abs_end and not processed:
                if sal_rec.get('EFFECTIVE_END_DATE'):
                    period_deduction = salary / 365 * ((datetime.strptime(sal_rec['EFFECTIVE_END_DATE'], '%Y-%m-%d %H:%M:%S') - salary_change).days + 1)
                else:
                    period_deduction = salary / 365 * ((abs_end - salary_change).days + 1)

                total_deduction += period_deduction

                if 'EFFECTIVE_END_DATE' in sal_rec and datetime.strptime(sal_rec['EFFECTIVE_END_DATE'], '%Y-%m-%d %H:%M:%S') < abs_end:
                    salary_change = datetime.strptime(sal_rec['EFFECTIVE_END_DATE'], '%Y-%m-%d %H:%M:%S') + timedelta(days=1)
                    processed = True
                else:
                    break

    return total_deduction

# Example test case
# print(uk_ps_ytd_salary_deduction(104, '2024-04-01 00:00:00', '2024-04-30 23:59:59', 'GB Maternity Leave', 'Bansal Groups_22_03_2024'))

# # Test cases for uk_ps_ytd_salary_deduction function
# print("Test Case 1: Valid employee number and date range")
# print("Expected output: Calculated YTD salary deduction based on data in MongoDB")
# print("Actual output:", uk_ps_ytd_salary_deduction('104', '2023-04-01 00:00:00', '2023-12-31 23:59:59', 'GB Maternity Leave', 'Bansal Groups_22_03_2024'), "\n")

# print("Test Case 2: Employee with no absence records")
# print("Expected output: 0")
# print("Actual output:", uk_ps_ytd_salary_deduction('104', '2023-04-01 00:00:00', '2023-12-31 23:59:59', 'GB Maternity Leave', 'Bansal Groups_22_03_2024'), "\n")

# ----------------------------------------------------------------------------------------------------

def fetch_tax_bands(tax_code_prefix):
    """
    Fetches tax bands from MongoDB for a given tax code prefix.

    Parameters:
    tax_code_prefix (str): The prefix of the tax code (e.g., 'S', '0T').

    Returns:
    list: A list of dictionaries containing tax bands and rates.
    """
    config = tax_config_collection.find_one({'TAX_CODE_PREFIX': tax_code_prefix})
    return config['BANDS'] if config else []

def calculate_tax_normal_with_codes5(tax_code, taxable_gross, pension_employee):
    tax_number = 0

    # Extract numeric part from the tax code
    numeric_part_match = re.search(r'\d+', tax_code)
    numeric_part = int(numeric_part_match.group()) if numeric_part_match else 0
    personal_allowance = math.ceil((numeric_part * 10) / 12)
    grossable_income = taxable_gross - personal_allowance

    # Validate tax code and extract prefix
    tax_code_prefix_match = re.match(r'[A-Z]+', tax_code)
    if tax_code_prefix_match:
        tax_code_prefix = tax_code_prefix_match.group()
    else:
        print(f"Invalid tax code: {tax_code}")
        return 0  # Return 0 tax if the tax code is invalid

    # Fetch tax bands from MongoDB based on the tax code prefix
    tax_bands = fetch_tax_bands(tax_code_prefix)

    # Check if tax bands are available
    if not tax_bands:
        print(f"No tax bands found for prefix: {tax_code_prefix}")
        return 0

    for band in tax_bands:
        if taxable_gross > band['UPPER_LIMIT']:
            tax_number += (band['UPPER_LIMIT'] - band['LOWER_LIMIT']) * band['RATE']
        elif taxable_gross > band['LOWER_LIMIT']:
            tax_number += (taxable_gross - band['LOWER_LIMIT']) * band['RATE']
            break

    return round(tax_number, 2)

# # Test cases for the updated function
# print("Test Case 1: S Tax Code")
# print("Expected output: Calculated tax based on MongoDB tax bands")
# print("Actual output:", calculate_tax_normal_with_codes5('S1250L', 5000, 200))

# print("\nTest Case 2: 0T Tax Code")
# print("Expected output: Calculated tax based on MongoDB tax bands")
# print("Actual output:", calculate_tax_normal_with_codes5('0T', 7000, 0))

# print("\nTest Case 3: BR Tax Code")
# print("Expected output: 20% of taxable gross")
# print("Actual output:", calculate_tax_normal_with_codes5('BR', 5000, 0))

# ---------------------------------------------------------------------------------------------------------



def calculate_tax_based_on_thresholds(grossable_income, start_threshold, thresholds):
    """
    Calculate tax based on the provided income thresholds.

    Parameters:
    grossable_income (float): The income to be taxed.
    start_threshold (float): The starting point for applying the thresholds.
    thresholds (list of tuples): Each tuple contains (upper limit, rate).

    Returns:
    float: The calculated tax amount.
    """
    tax_amount = 0
    for upper_limit, rate in thresholds:
        if grossable_income > upper_limit:
            tax_amount += (upper_limit - start_threshold) * rate
            start_threshold = upper_limit
        else:
            tax_amount += (grossable_income - start_threshold) * rate
            break
    return tax_amount

def calculate_tax_normal_with_codes8(tax_code, taxable_gross, taxable_gross_till_date, paye_till_date, month_number):
    tax_number = 0

    # Extract numeric part from the tax code
    numeric_part_match = re.search(r'\d+', tax_code)
    numeric_part = int(numeric_part_match.group()) if numeric_part_match else 0

    # Extract tax code prefix (handle missing prefixes)
    tax_code_prefix = re.match(r'[A-Z]+', tax_code)
    if tax_code_prefix:
        tax_code_prefix = tax_code_prefix.group()
    else:
        tax_code_prefix = tax_code

    # Fetch tax bands from MongoDB based on the tax code prefix
    tax_bands = fetch_tax_bands(tax_code_prefix)

    if tax_code.startswith('S'):
        grossable_income = taxable_gross - math.ceil((numeric_part * 10) / 12)
        tax_number = calculate_tax_based_on_thresholds(taxable_gross, grossable_income, tax_bands)

    elif 'L' in tax_code or 'T' in tax_code or 'M' in tax_code or 'N' in tax_code:
        grossable_income = taxable_gross + taxable_gross_till_date - month_number * (math.ceil((numeric_part * 10) / 12) + 0.76)
        tax_number = calculate_tax_based_on_thresholds(grossable_income, 0, tax_bands)
        tax_number -= paye_till_date

    elif tax_code == 'BR':
        tax_number = 0.2 * taxable_gross
    elif tax_code == 'D0':
        tax_number = 0.4 * taxable_gross
    elif tax_code == 'D1':
        tax_number = 0.45 * taxable_gross

    return tax_number

# # Test cases for the updated function
# print("Test Case 1: S Tax Code")
# print("Expected output: Calculated tax based on MongoDB tax bands")
# print("Actual output:", calculate_tax_normal_with_codes8('S1250L', 5000, 2000, 100, 1))

# print("\nTest Case 2: L Tax Code")
# print("Expected output: Calculated tax based on MongoDB tax bands")
# print("Actual output:", calculate_tax_normal_with_codes8('1250L', 7000, 2000, 500, 2))

# print("\nTest Case 3: BR Tax Code")
# print("Expected output: 20% of taxable gross")
# print("Actual output:", calculate_tax_normal_with_codes8('BR', 5000, 0, 0, 1))


# ---------------------------------------------------------------------------------------------

# from datetime import datetime, timedelta

def get_previous_month_end(v_start_date):
    """
    Subtracts a day from the given string date and returns the result as a string.

    Parameters:
    v_start_date (str): The start date in 'YYYY-MM-DD HH:MM:SS' format.

    Returns:
    str: The previous day's date in 'YYYY-MM-DD HH:MM:SS' format.
    """
    # Convert the string to a datetime object
    start_date_dt = datetime.strptime(v_start_date, '%Y-%m-%d %H:%M:%S')
    
    # Subtract one day
    previous_month_end = start_date_dt - timedelta(days=1)
    
    # Convert back to string in the same format
    v_previous_month_end = previous_month_end.strftime('%Y-%m-%d %H:%M:%S')
    
    return v_previous_month_end

# Example usage
# v_start_date = "2024-04-30 00:00:00"
# v_previous_month_end = get_previous_month_end(v_start_date)
# print(f"Previous month end: {v_previous_month_end}")
