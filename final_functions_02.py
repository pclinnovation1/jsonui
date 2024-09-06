from pymongo import MongoClient
from datetime import datetime, timedelta
from dateutil import parser
import config  # Import the configuration file
import pandas as pd
import numpy as np

from final_functions_01 import uk_ps_absence_entitlement_days_1, uk_ps_absence_entitlement_days

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
payroll_periods_collection = db[config.COLLECTIONS['payroll_periods']]
migration_data_collection = db[config.COLLECTIONS['migration_data']]
balance_calculation_report_collection = db[config.COLLECTIONS['balance_calculation_report']]
pension_details_collection = db[config.COLLECTIONS['pension_details']]
employee_information_collection = db[config.COLLECTIONS['employee_information']]
tax_codes_collection = db[config.COLLECTIONS['tax_codes']]

# migration_data_collection = db[config.COLLECTIONS['migration_data']]


# -------------------------------------------------------------------------------------------------------------


# def fetch_dates_from_db(v_payroll_period, v_client_id):
#     """
#     Fetches dates related to a payroll period and client ID from MongoDB.

#     Parameters:
#     v_payroll_period (str): The payroll period name modified.
#     v_client_id (str): The client identifier.

#     Returns:
#     list: A list containing start date, end date, payroll run date, cutoff date, and month number.
#     """
#     print(f"Fetching dates for payroll period: {v_payroll_period} and client ID: {v_client_id}")
    
#     # Fetch dates from MongoDB
#     result = payroll_periods_collection.find_one({
#         "PERIOD_NAME_MODIFIED": v_payroll_period,
#         "CLIENT_ID": v_client_id
#     }, {"START_DATE": 1, "END_DATE": 1, "PAYROLL_RUN_DATE": 1, "CUTOFF_DATE": 1, "MONTH_NUMBER": 1})

#     if result:
#         # Convert string dates to datetime objects if they exist
#         dates = [
#             datetime.strptime(result.get('START_DATE'), '%Y-%m-%d %H:%M:%S') if result.get('START_DATE') else None,
#             datetime.strptime(result.get('END_DATE'), '%Y-%m-%d %H:%M:%S') if result.get('END_DATE') else None,
#             datetime.strptime(result.get('PAYROLL_RUN_DATE'), '%Y-%m-%d %H:%M:%S') if result.get('PAYROLL_RUN_DATE') else None,
#             datetime.strptime(result.get('CUTOFF_DATE'), '%Y-%m-%d %H:%M:%S') if result.get('CUTOFF_DATE') else None,
#             int(result.get('MONTH_NUMBER')) if result.get('MONTH_NUMBER') is not None else None
#         ]

#         print(f"Fetched dates: {dates}")
#         return dates
#     else:
#         raise Exception("No data found")

# # Test cases for fetch_dates_from_db function
# print("Test Case 1: Valid payroll period and client ID")
# try:
#     dates = fetch_dates_from_db("1 2024 Calendar Month", "Bansal Groups_22_03_2024")
#     print("Fetched dates:", dates)
# except Exception as e:
#     print("Error:", e)

def fetch_dates_from_db(v_payroll_period, v_client_id):
    """
    Fetches dates related to a payroll period and client ID from MongoDB in string format.

    Parameters:
    v_payroll_period (str): The payroll period name modified.
    v_client_id (str): The client identifier.

    Returns:
    list: A list containing start date, end date, payroll run date, cutoff date, and month number as strings.
    """
    print(f"Fetching dates for payroll period: {v_payroll_period} and client ID: {v_client_id}")
    
    # Fetch dates from MongoDB
    result = payroll_periods_collection.find_one({
        "PERIOD_NAME_MODIFIED": v_payroll_period,
        "CLIENT_ID": v_client_id
    }, {"START_DATE": 1, "END_DATE": 1, "PAYROLL_RUN_DATE": 1, "CUTOFF_DATE": 1, "MONTH_NUMBER": 1})

    if result:
        # Return the dates as they are (strings)
        dates = [
            result.get('START_DATE'),  # Keep as string
            result.get('END_DATE'),    # Keep as string
            result.get('PAYROLL_RUN_DATE'),  # Keep as string
            result.get('CUTOFF_DATE'),  # Keep as string
            result.get('MONTH_NUMBER')  # Keep as is (should be an integer)
        ]

        print(f"Fetched dates: {dates}")
        return dates
    else:
        raise Exception("No data found")


# print("\nTest Case 2: Invalid payroll period")
# try:
#     dates = fetch_dates_from_db("3 2024 Calendar Month", "Bansal Groups_22_03_2024")
#     print("Fetched dates:", dates)
# except Exception as e:
#     print("Error:", e)

# print("\nTest Case 3: Valid payroll period but non-existent client ID")
# try:
#     dates = fetch_dates_from_db("5 2024 Calendar Month", "Bansal Groups_22_03_2024")
#     print("Fetched dates:", dates)
# except Exception as e:
#     print("Error:", e)


# ---------------------------------------------------------------------------------------------------------------


def fetch_hire_dates_from_db(vemp_num, v_client_id):
    """
    Fetches the hire date for a specific employee number and client ID from MongoDB.

    Parameters:
    vemp_num (str): The employee number.
    v_client_id (str): The client identifier.

    Returns:
    str: The hire date in string format or None if no record is found.
    """
    print(f"Fetching hire date for employee number: {vemp_num} and client ID: {v_client_id}")

    # Fetch hire date from MongoDB
    result = migration_data_collection.find_one({
        "EMPLOYEE_NUMBER": vemp_num,
        "CLIENT_ID": v_client_id
    }, {"hire_date": 1})

    if result and 'hire_date' in result:
        print(f"Hire date found: {result['hire_date']}")
        return result['hire_date']
    else:
        print("No hire date found.")
        return None

# # Test cases for fetch_hire_dates_from_db function
# print("Test Case 1: Valid employee number and client ID")
# hire_date = fetch_hire_dates_from_db("101", "client_001")
# print("Fetched hire date:", hire_date)

# print("\nTest Case 2: Invalid employee number")
# hire_date = fetch_hire_dates_from_db("INVALID_EMP", "client_001")
# print("Fetched hire date:", hire_date)

# print("\nTest Case 3: Valid employee number but non-existent client ID")
# hire_date = fetch_hire_dates_from_db("101", "non_existent_client")
# print("Fetched hire date:", hire_date)


# ----------------------------------------------------------------------------------------------------------------

def fetch_latest_salary_update(emp_num, end_date, payroll_process_date, client_id):

    # Convert end_date and payroll_process_date to datetime objects if they are not already
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    if isinstance(payroll_process_date, str):
        payroll_process_date = datetime.strptime(payroll_process_date, '%Y-%m-%d')

    # Query MongoDB to fetch the latest salary update
    query = {
        "EMPLOYEE_NUMBER": emp_num,
        "EFFECTIVE_START_DATE": {"$lte": end_date},
        "SALARY_CREATION_DATE": {"$lte": payroll_process_date},
        "CLIENT_ID": client_id
    }

    # Sort the results by EFFECTIVE_START_DATE in descending order and get the first record
    result = salary_details_collection.find(query).sort("EFFECTIVE_START_DATE", -1).limit(1)

    latest_salary_date = None
    if result.count() > 0:
        latest_salary_date = result[0].get('SALARY_CREATION_DATE')
        # Convert the date from MongoDB to datetime object if it is in string format
        if isinstance(latest_salary_date, str):
            latest_salary_date = datetime.strptime(latest_salary_date, '%Y-%m-%d %H:%M:%S')

    return latest_salary_date

# # Test cases for fetch_latest_salary_update function
# print("Test Case 1: Valid employee number and dates")
# print("Expected output: A datetime object representing the latest salary creation date")
# print("Actual output:", fetch_latest_salary_update('EMP123', '2023-06-30', '2023-06-15', 'client_001'), "\n")

# print("Test Case 2: Employee number with no matching records")
# print("Expected output: None")
# print("Actual output:", fetch_latest_salary_update('NON_EXISTENT_EMP', '2023-06-30', '2023-06-15', 'client_001'), "\n")

# print("Test Case 3: Invalid date formats")
# print("Expected output: None or an error if date parsing fails")
# print("Actual output:", fetch_latest_salary_update('EMP123', 'invalid_date', 'invalid_date', 'client_001'), "\n")

# ---------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------


def uk_ps_ytd_absence_entitlement_2(v_emp_num, p_ytd_start_date, p_ytd_end_date, v_payroll_process_date, v_client_id):
    """
    Calculate YTD absence entitlement for an employee using MongoDB.

    Parameters:
    - v_emp_num: Employee number
    - p_ytd_start_date: YTD start date (string format 'YYYY-MM-DD')
    - p_ytd_end_date: YTD end date (string format 'YYYY-MM-DD')
    - v_payroll_process_date: Payroll process date
    - v_client_id: Client identifier

    Returns:
    - Total YTD absence entitlement
    """
    v_total_ytd_absence_entitlement = 0
    v_ytd_start_date = datetime.strptime(p_ytd_start_date, '%Y-%m-%d')
    v_ytd_end_date = datetime.strptime(p_ytd_end_date, '%Y-%m-%d')
    v_current_date = v_ytd_start_date.replace(day=1)

    while v_current_date <= v_ytd_end_date.replace(day=1):
        v_start_date = v_current_date.replace(day=1)
        v_end_date = (v_current_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        # Fetch latest salary update date
        v_sal_last_update_date = fetch_latest_salary_update(v_emp_num, v_end_date, v_payroll_process_date, v_client_id)
        print(f"Latest Salary Update Date for {v_emp_num}: {v_sal_last_update_date}")

        # Fetch annual salary
        v_annual_salary = fetch_annual_salary(v_emp_num, v_sal_last_update_date, v_client_id)
        print(f"Annual Salary for {v_emp_num} as of {v_sal_last_update_date}: {v_annual_salary}")

        if v_ytd_end_date.month == v_end_date.month:
            v_absence_entitlement_days = uk_ps_absence_entitlement_days_1(v_emp_num, v_start_date, v_end_date, v_payroll_process_date, v_client_id)
        else:
            v_absence_entitlement_days = uk_ps_absence_entitlement_days(v_emp_num, v_start_date, v_end_date, v_payroll_process_date, v_client_id)

        print(f"Absence Entitlement Days for {v_emp_num} from {v_start_date} to {v_end_date}: {v_absence_entitlement_days}")

        # Calculate monthly absence entitlement
        v_monthly_absence_entitlement = (v_absence_entitlement_days * v_annual_salary / 260)
        v_total_ytd_absence_entitlement += v_monthly_absence_entitlement

        print(f"Monthly Absence Entitlement: {v_monthly_absence_entitlement}")
        print(f"Total YTD Absence Entitlement so far: {v_total_ytd_absence_entitlement}")

        # Move to the next month
        v_current_date = v_current_date.replace(day=1) + timedelta(days=32)

    return v_total_ytd_absence_entitlement

# # Test cases for uk_ps_ytd_absence_entitlement_2 function
# print("Test Case 1: Valid employee number and dates")
# print("Expected output: A float value representing the total YTD absence entitlement")
# print("Actual output:", uk_ps_ytd_absence_entitlement_2('EMP123', '2023-01-01', '2023-12-31', '2023-06-30', 'client_001'), "\n")

# print("Test Case 2: Employee number with no matching records")
# print("Expected output: 0.0")
# print("Actual output:", uk_ps_ytd_absence_entitlement_2('NON_EXISTENT_EMP', '2023-01-01', '2023-12-31', '2023-06-30', 'client_001'), "\n")

# print("Test Case 3: Invalid date format")
# print("Expected output: Error or 0.0")
# print("Actual output:", uk_ps_ytd_absence_entitlement_2('EMP123', 'invalid_date', '2023-12-31', '2023-06-30', 'client_001'), "\n")






# -----------------------------------------------------------------------------------------------------------------

def fetch_last_payroll_period(v_start_date, v_client_id):
    """
    Fetches the last payroll period name for a given start date and client ID from MongoDB.
    """

    print(f"Fetching last payroll period for start date: {v_start_date} and client ID: {v_client_id}")

    # Attempt to convert input dates to datetime objects if they are strings
    try:
        if isinstance(v_start_date, str):
            v_start_date = datetime.strptime(v_start_date, '%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        print(f"Error converting start date: {e}")
        return None

    # Subtract one day to get the previous month's end date
    previous_month_end = v_start_date - timedelta(days=1)
    print(f"Previous month end date: {previous_month_end}")

    # Debugging: Print the query criteria
    print("Querying MongoDB with:")
    print(f"End Date: {previous_month_end}, Client ID: {v_client_id}")

    # Query MongoDB to fetch the last payroll period
    result = db.UK_PS_PAYROLL_PERIODS.find_one({
        "END_DATE": previous_month_end.strftime('%Y-%m-%d %H:%M:%S'),
        "CLIENT_ID": v_client_id
    }, {"PERIOD_NAME_MODIFIED": 1})

    # Debugging: Print the fetched data
    print("Fetched data:", result)

    if result and 'PERIOD_NAME_MODIFIED' in result:
        print(f"Fetched last payroll period: {result['PERIOD_NAME_MODIFIED']}")
        return result['PERIOD_NAME_MODIFIED']
    else:
        print("No last payroll period found.")
        return None

# # Test cases for fetch_last_payroll_period function
# print("Test Case 1: Valid start date and client ID")
# last_payroll_period = fetch_last_payroll_period("2024-04-01 00:00:00", "Bansal Groups_22_03_2024")
# print("Fetched last payroll period:", last_payroll_period)

# print("\nTest Case 2: Invalid start date format")
# last_payroll_period = fetch_last_payroll_period("2024-05-01 00:00:00", "Bansal Groups_22_03_2024")
# print("Fetched last payroll period:", last_payroll_period)

# -----------------------------------------------------------------------------------------------------------------

def fetch_salary_creation_date(v_emp_num, v_end_date, v_payroll_process_date, v_client_id):
    """
    Fetches the salary creation date for a given employee number, end date, payroll process date, and client ID from MongoDB.

    Parameters:
    v_emp_num (str): The employee number.
    v_end_date (str): The end date for which to fetch the salary creation date (in 'YYYY-MM-DD HH:MM:SS' format).
    v_payroll_process_date (str): The payroll process date (in 'YYYY-MM-DD HH:MM:SS' format).
    v_client_id (str): The client identifier.

    Returns:
    str: The salary creation date or None if no record is found.
    """
    print(f"Fetching salary creation date for employee number: {v_emp_num}, end date: {v_end_date}, payroll process date: {v_payroll_process_date}, and client ID: {v_client_id}")

    # print(f"details type: {type(v_emp_num)}, end date: {type(v_end_date)}, payroll process date: {type(v_payroll_process_date)}, and client ID: {type(v_client_id)}")

    # Query MongoDB to fetch the salary creation date
    result = salary_details_collection.find_one(
        {
            "EMPLOYEE_NUMBER": v_emp_num,
            "EFFECTIVE_START_DATE": {"$lte": v_end_date},  # String-based comparison
            "SALARY_CREATION_DATE": {"$lte": v_payroll_process_date},  # String-based comparison
            "CLIENT_ID": v_client_id
        },
        sort=[("EFFECTIVE_START_DATE", -1)]  # Sort by EFFECTIVE_START_DATE descending
    )
    # print("result: ", result)

    if result and 'SALARY_CREATION_DATE' in result:
        print(f"Fetched salary creation date: {result['SALARY_CREATION_DATE']}")
        return result['SALARY_CREATION_DATE']
    else:
        print("No salary creation date found.")
        return None

# # Test cases for fetch_salary_creation_date function
# print("Test Case 1: Valid employee number, end date, payroll process date, and client ID")
# salary_creation_date = fetch_salary_creation_date(104, "2024-04-30 00:00:00", "2024-04-29 00:00:00", "Bansal Groups_22_03_2024")
# print("Fetched salary creation date:", salary_creation_date)

# print("\nTest Case 2:")
# salary_creation_date = fetch_salary_creation_date(101, "2024-04-30 00:00:00", "2024-04-29 00:00:00", "Bansal Groups_22_03_2024")
# print("Fetched salary creation date:", salary_creation_date)

# print("\nTest Case 3:")
# salary_creation_date = fetch_salary_creation_date(102, "2024-04-30 00:00:00", "2024-04-29 00:00:00", "Bansal Groups_22_03_2024")
# print("Fetched salary creation date:", salary_creation_date)


# ----------------------------------------------------------------------------------------------------------


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

# ------------------------------------------------------------------------------------------------------------

def fetch_maternity_leave_dates(v_emp_num, v_client_id):
    """
    Fetches maternity leave dates for a given employee number and client ID from MongoDB.

    Parameters:
    v_emp_num (str): The employee number.
    v_client_id (str): The client identifier.

    Returns:
    list of dict: A list of dictionaries containing maternity leave start and end dates.
    """
    print(f"Fetching maternity leave dates for employee number: {v_emp_num} and client ID: {v_client_id}")

    # Connect to MongoDB
    client = get_mongo_connection()
    db = client['oras']

    # Query MongoDB to fetch maternity leave dates
    results = list(absence_details_collection.find(
        {
            "EMPLOYEE_ID": v_emp_num,
            "LEAVE_TYPE": "GB Maternity Leave",
            "CLIENT_ID": v_client_id
        },
        projection={"LEAVE_START_DATE_TIME": 1, "LEAVE_END_DATE_TIME": 1}
    ))

    leave_dates = [(res['LEAVE_START_DATE_TIME'], res['LEAVE_END_DATE_TIME']) for res in results]
    print(f"Fetched maternity leave dates: {leave_dates}")

    return leave_dates

def fetch_previous_maternity_ytd(v_emp_num, v_last_payroll_period, v_client_id):
    """
    Fetches the previous year-to-date maternity balance for a given employee number, last payroll period, and client ID from MongoDB.

    Parameters:
    v_emp_num (str): The employee number.
    v_last_payroll_period (str): The last payroll period.
    v_client_id (str): The client identifier.

    Returns:
    float: The year-to-date maternity balance or 0 if no record is found.
    """
    print(f"Fetching previous maternity YTD for employee number: {v_emp_num}, last payroll period: {v_last_payroll_period}, and client ID: {v_client_id}")

    # Query MongoDB to fetch the previous maternity YTD
    result = balance_calculation_report_collection.find_one(
        {
            "EMPLOYEE_NUMBER": v_emp_num,
            "BALANCE_CATEGORY": "Absences",
            "ELEMENT_NAME": "Statutory Maternity",
            "PAYROLL_PERIOD": v_last_payroll_period,
            "CLIENT_ID": v_client_id
        },
        projection={"YEAR_TO_DATE": 1}
    )

    ytd_value = result['YEAR_TO_DATE'] if result and 'YEAR_TO_DATE' in result else 0
    print(f"Fetched previous maternity YTD: {ytd_value}")

    return ytd_value

# # Test cases for fetch_maternity_leave_dates function
# print("Test Case 1: Fetch maternity leave dates")
# maternity_leave_dates = fetch_maternity_leave_dates("101", "Bansal Groups_22_03_2024")
# print("Fetched maternity leave dates:", maternity_leave_dates)

# # Test cases for fetch_previous_maternity_ytd function
# print("\nTest Case 2: Fetch previous maternity YTD")
# previous_maternity_ytd = fetch_previous_maternity_ytd("104", "3 2024 Calendar Month", "Bansal Groups_22_03_2024")
# print("Fetched previous maternity YTD:", previous_maternity_ytd)


# -------------------------------------------------------------------------------------------------------------

def fetch_paternity_leave_dates(v_emp_num, v_client_id):
    """
    Fetches paternity leave dates for a given employee number and client ID from MongoDB.

    Parameters:
    v_emp_num (str): The employee number.
    v_client_id (str): The client identifier.

    Returns:
    list of tuple: A list of tuples containing paternity leave start and end dates.
    """
    print(f"Fetching paternity leave dates for employee number: {v_emp_num} and client ID: {v_client_id}")

    # Query MongoDB to fetch paternity leave dates
    results = list(absence_details_collection.find(
        {
            "EMPLOYEE_ID": v_emp_num,
            "LEAVE_TYPE": "GB Paternity Leave",
            "CLIENT_ID": v_client_id
        },
        projection={"LEAVE_START_DATE_TIME": 1, "LEAVE_END_DATE_TIME": 1}
    ))

    leave_dates = [(res['LEAVE_START_DATE_TIME'], res['LEAVE_END_DATE_TIME']) for res in results]
    print(f"Fetched paternity leave dates: {leave_dates}")

    return leave_dates

def fetch_sickness_leave_dates(v_emp_num, v_client_id):
    """
    Fetches sickness leave dates for a given employee number and client ID from MongoDB.

    Parameters:
    v_emp_num (str): The employee number.
    v_client_id (str): The client identifier.

    Returns:
    list of tuple: A list of tuples containing sickness leave start and end dates.
    """
    print(f"Fetching sickness leave dates for employee number: {v_emp_num} and client ID: {v_client_id}")

    # Query MongoDB to fetch sickness leave dates
    results = list(absence_details_collection.find(
        {
            "EMPLOYEE_ID": v_emp_num,
            "LEAVE_TYPE": "GB2 Sickness",
            "CLIENT_ID": v_client_id
        },
        projection={"LEAVE_START_DATE_TIME": 1, "LEAVE_END_DATE_TIME": 1}
    ))

    leave_dates = [(res['LEAVE_START_DATE_TIME'], res['LEAVE_END_DATE_TIME']) for res in results]
    print(f"Fetched sickness leave dates: {leave_dates}")

    return leave_dates

# # Test cases for fetch_paternity_leave_dates function
# print("Test Case 1: Fetch paternity leave dates")
# paternity_leave_dates = fetch_paternity_leave_dates("101", "Bansal Groups_22_03_2024")
# print("Fetched paternity leave dates:", paternity_leave_dates)

# # Test cases for fetch_sickness_leave_dates function
# print("\nTest Case 2: Fetch sickness leave dates")
# sickness_leave_dates = fetch_sickness_leave_dates("104", "Bansal Groups_22_03_2024")
# print("Fetched sickness leave dates:", sickness_leave_dates)

# ----------------------------------------------------------------------------------------------

def fetch_absence_entitlement_retro(v_emp_num, v_payroll_period, v_client_id):
    """
    Fetches the absence entitlement retroactive value for a given employee number, payroll period, and client ID from MongoDB.

    Parameters:
    v_emp_num (str): The employee number.
    v_payroll_period (str): The payroll period.
    v_client_id (str): The client identifier.

    Returns:
    float: The current value of the absence entitlement retroactive.
    """
    print(f"Fetching absence entitlement retroactive for employee number: {v_emp_num}, payroll period: {v_payroll_period}, and client ID: {v_client_id}")

    # Query MongoDB to fetch the current value of the absence entitlement retroactive
    result = balance_calculation_report_collection.find_one(
        {
            "EMPLOYEE_NUMBER": v_emp_num,
            "BALANCE_CATEGORY": "Absences",
            "ELEMENT_NAME": "Annual Leaves Days Entitlement Retroactive",
            "CLIENT_ID": v_client_id,
            "PAYROLL_PERIOD": v_payroll_period
        },
        projection={"CURRENT_VALUE": 1}
    )

    current_value = result['CURRENT_VALUE'] if result else 0
    print(f"Fetched absence entitlement retroactive value: {current_value}")

    return current_value

def fetch_absence_entitlement_retro_ytd(v_emp_num, v_payroll_period, v_client_id):
    """
    Fetches the year-to-date absence entitlement retroactive value for a given employee number, payroll period, and client ID from MongoDB.

    Parameters:
    v_emp_num (str): The employee number.
    v_payroll_period (str): The payroll period.
    v_client_id (str): The client identifier.

    Returns:
    float: The year-to-date value of the absence entitlement retroactive.
    """
    print(f"Fetching YTD absence entitlement retroactive for employee number: {v_emp_num}, payroll period: {v_payroll_period}, and client ID: {v_client_id}")

    # Query MongoDB to fetch the year-to-date value of the absence entitlement retroactive
    result = balance_calculation_report_collection.find_one(
        {
            "EMPLOYEE_NUMBER": v_emp_num,
            "BALANCE_CATEGORY": "Absences",
            "ELEMENT_NAME": "Annual Leaves Days Entitlement Retroactive",
            "CLIENT_ID": v_client_id,
            "PAYROLL_PERIOD": v_payroll_period
        },
        projection={"YEAR_TO_DATE": 1}
    )

    ytd_value = result['YEAR_TO_DATE'] if result else 0
    print(f"Fetched YTD absence entitlement retroactive value: {ytd_value}")

    return ytd_value

# # Test cases for fetch_absence_entitlement_retro function
# print("Test Case 1: Fetch absence entitlement retroactive")
# absence_entitlement_retro = fetch_absence_entitlement_retro("104", "3 2024 Calendar Month", "Bansal Groups_22_03_2024")
# print("Fetched absence entitlement retroactive:", absence_entitlement_retro)

# # Test cases for fetch_absence_entitlement_retro_ytd function
# print("\nTest Case 2: Fetch YTD absence entitlement retroactive")
# absence_entitlement_retro_ytd = fetch_absence_entitlement_retro_ytd("104", "3 2024 Calendar Month", "Bansal Groups_22_03_2024")
# print("Fetched YTD absence entitlement retroactive:", absence_entitlement_retro_ytd)

# ---------------------------------------------------------------------------------------------------

def fetch_salary_ytd_previous_period(v_emp_num, v_last_payroll_period, v_client_id):
    """
    Fetches the Year-to-Date (YTD) salary for the previous payroll period for a given employee number and client ID from MongoDB.

    Parameters:
    v_emp_num (str): The employee number.
    v_last_payroll_period (str): The last payroll period.
    v_client_id (str): The client identifier.

    Returns:
    float: The YTD salary for the previous payroll period.
    """
    print(f"Fetching YTD salary for previous period for employee number: {v_emp_num}, last payroll period: {v_last_payroll_period}, and client ID: {v_client_id}")

    # Query MongoDB to fetch the YTD salary for the previous payroll period
    result = balance_calculation_report_collection.find_one(
        {
            "EMPLOYEE_NUMBER": v_emp_num,
            "BALANCE_CATEGORY": "Regular Earnings",
            "ELEMENT_NAME": "Salary",
            "CLIENT_ID": v_client_id,
            "PAYROLL_PERIOD": v_last_payroll_period
        },
        projection={"YEAR_TO_DATE": 1}
    )

    ytd_salary = result['YEAR_TO_DATE'] if result else 0
    print(f"Fetched YTD salary for previous period: {ytd_salary}")

    return ytd_salary

# # Test case for fetch_salary_ytd_previous_period function
# print("Test Case: Fetch YTD salary for previous payroll period")
# salary_ytd_previous_period = fetch_salary_ytd_previous_period("104", "3 2024 Calendar Month", "Bansal Groups_22_03_2024")
# print("Fetched YTD salary for previous payroll period:", salary_ytd_previous_period)


# ----------------------------------------------------------------------------------------------------

def fetch_pension_contribution(v_emp_num, v_payroll_period, v_client_id):
    """
    Fetches the total pension contribution for a given employee number, payroll period, and client ID from MongoDB.

    Parameters:
    v_emp_num (str): The employee number.
    v_payroll_period (str): The payroll period.
    v_client_id (str): The client identifier.

    Returns:
    float: The total pension contribution for the specified criteria.
    """
    print(f"Fetching pension contribution for employee number: {v_emp_num}, payroll period: {v_payroll_period}, and client ID: {v_client_id}")

    # Query MongoDB to fetch the total pension contribution
    pipeline = [
        {
            "$match": {
                "EMPLOYEE_NUMBER": v_emp_num,
                "BALANCE_CATEGORY": {"$in": ["Regular Earnings", "Absences"]},
                "ELEMENT_NAME": {"$nin": [
                    "Occupational Sickness Retroactive",
                    "TRG Sickness Occupational Plan Entitlement Payment",
                    "Annual Leaves Days Final Disbursement Payment",
                    "Annual Leaves Days Final Disbursement Retroactive",
                    "Annual Leaves Hourly Final Disbursement Payment",
                    "Annual Leaves Hourly Final Disbursement Retroactive",
                    "Occupational Maternity",
                    "Occupational Maternity Retroactive",
                    "Statutory Paternity Retroactive",
                    "Statutory Sickness",
                    "Statutory Sickness Retroactive"
                ]},
                "PAYROLL_PERIOD": v_payroll_period,
                "CLIENT_ID": v_client_id
            }
        },
        {
            "$group": {
                "_id": None,
                "total_contribution": {"$sum": "$CURRENT_VALUE"}
            }
        }
    ]

    result = list(balance_calculation_report_collection.aggregate(pipeline))

    total_contribution = result[0]['total_contribution'] if result else 0
    print(f"Fetched pension contribution: {total_contribution}")

    return total_contribution

# # Test case for fetch_pension_contribution function
# print("Test Case: Fetch pension contribution")
# pension_contribution = fetch_pension_contribution("104", "3 2024 Calendar Month", "Bansal Groups_22_03_2024")
# print("Fetched pension contribution:", pension_contribution)



def fetch_pension_details(v_emp_num, v_client_id):
    """
    Fetches employer and employee pension contributions for a given employee and client from MongoDB.

    Parameters:
    v_emp_num (str): The employee number.
    v_client_id (str): The client identifier.

    Returns:
    tuple: Employer and employee pension contributions.
    """
    print(f"Fetching pension details for employee number: {v_emp_num} and client ID: {v_client_id}")

    # Query MongoDB to fetch pension details
    result = pension_details_collection.find_one(
        {"EMPLOYEE_NUMBER": v_emp_num, "CLIENT_ID": v_client_id},
        {"EMPLOYER_CONTRIBUTION": 1, "EMPLOYEE_CONTRIBUTION": 1}
    )

    if result:
        employer_contribution = result.get("EMPLOYER_CONTRIBUTION", 0)
        employee_contribution = result.get("EMPLOYEE_CONTRIBUTION", 0)
        print(f"Fetched employer contribution: {employer_contribution}, employee contribution: {employee_contribution}")
        return employer_contribution, employee_contribution
    else:
        print("No pension details found. Returning default values.")
        return 0, 0

def fetch_pension_ytd(v_emp_num, balance_category, element_name, v_last_payroll_period, v_client_id):
    """
    Fetches the year-to-date (YTD) pension data for a given employee, balance category, element name, payroll period, and client from MongoDB.

    Parameters:
    v_emp_num (str): The employee number.
    balance_category (str): The balance category.
    element_name (str): The element name.
    v_last_payroll_period (str): The last payroll period.
    v_client_id (str): The client identifier.

    Returns:
    float: The year-to-date (YTD) pension data.
    """
    print(f"Fetching YTD pension data for employee number: {v_emp_num}, balance category: {balance_category}, element name: {element_name}, payroll period: {v_last_payroll_period}, and client ID: {v_client_id}")

    # Query MongoDB to fetch YTD pension data
    result = balance_calculation_report_collection.find_one(
        {
            "EMPLOYEE_NUMBER": v_emp_num,
            "BALANCE_CATEGORY": balance_category,
            "ELEMENT_NAME": element_name,
            "PAYROLL_PERIOD": v_last_payroll_period,
            "CLIENT_ID": v_client_id
        },
        {"YEAR_TO_DATE": 1}
    )

    ytd_value = result.get("YEAR_TO_DATE", 0) if result else 0
    print(f"Fetched YTD pension data: {ytd_value}")

    return ytd_value

# # Test cases for fetch_pension_details and fetch_pension_ytd functions
# print("Test Case: Fetch pension details")
# pension_details = fetch_pension_details("104", "Bansal Groups_22_03_2024")
# print("Fetched pension details:", pension_details)

# print("\nTest Case: Fetch YTD pension data")
# pension_ytd = fetch_pension_ytd("104", "Regular Earnings", "Pension", "3 2024 Calendar Month", "Bansal Groups_22_03_2024")
# print("Fetched YTD pension data:", pension_ytd)


# --------------------------------------------------------------------------------------------------------------------------


def fetch_pre_statutory_deduction(v_emp_num, v_payroll_period, v_client_id):
    """
    Fetches the sum of 'Pre-Statutory Deductions Without Pension' for a given employee and payroll period from MongoDB.

    Parameters:
    v_emp_num (str): The employee number.
    v_payroll_period (str): The payroll period.
    v_client_id (str): The client identifier.

    Returns:
    float: The sum of pre-statutory deductions.
    """
    print(f"Fetching pre-statutory deductions for employee number: {v_emp_num}, payroll period: {v_payroll_period}, and client ID: {v_client_id}")

    # Query MongoDB to fetch pre-statutory deductions
    result = balance_calculation_report_collection.aggregate([
        {
            "$match": {
                "EMPLOYEE_NUMBER": v_emp_num,
                "BALANCE_CATEGORY": "Pre-Statutory Deductions Without Pension",
                "PAYROLL_PERIOD": v_payroll_period,
                "CLIENT_ID": v_client_id
            }
        },
        {
            "$group": {
                "_id": None,
                "total_deduction": {"$sum": "$CURRENT_VALUE"}
            }
        }
    ])

    # Extract result from aggregation
    result = list(result)  # Convert cursor to list
    total_deduction = result[0]['total_deduction'] if result else 0
    print(f"Fetched total pre-statutory deductions: {total_deduction}")

    return total_deduction

def fetch_niable_gross_till_date(v_emp_num, v_last_payroll_period, v_client_id):
    """
    Fetches the year-to-date (YTD) 'NI_GROSS' value for National Insurance Deductions from MongoDB.

    Parameters:
    v_emp_num (str): The employee number.
    v_last_payroll_period (str): The last payroll period.
    v_client_id (str): The client identifier.

    Returns:
    float: The year-to-date NI gross value.
    """
    print(f"Fetching NI gross till date for employee number: {v_emp_num}, last payroll period: {v_last_payroll_period}, and client ID: {v_client_id}")

    # Query MongoDB to fetch NI gross till date
    result = balance_calculation_report_collection.find_one(
        {
            "EMPLOYEE_NUMBER": v_emp_num,
            "ELEMENT_NAME": "NI_GROSS",
            "BALANCE_CATEGORY": "National Insaurance Deductions",
            "PAYROLL_PERIOD": v_last_payroll_period,
            "CLIENT_ID": v_client_id
        },
        {"YEAR_TO_DATE": 1}
    )

    niable_gross = result.get("YEAR_TO_DATE", 0) if result else 0
    print(f"Fetched NI gross till date: {niable_gross}")

    return niable_gross

# # Test cases for the updated MongoDB functions
# print("Test Case: Fetch pre-statutory deduction")
# pre_statutory_deduction = fetch_pre_statutory_deduction("E123", "3 2024 Calendar Month", "client_001")
# print("Fetched pre-statutory deduction:", pre_statutory_deduction)

# print("\nTest Case: Fetch NI gross till date")
# niable_gross_till_date = fetch_niable_gross_till_date("E123", "3 2024 Calendar Month", "client_001")
# print("Fetched NI gross till date:", niable_gross_till_date)

# -----------------------------------------------------------------------------------------------------------------------------

def fetch_ni_category(v_emp_num, v_client_id):
    """
    Fetches the National Insurance (NI) category for a given employee from MongoDB.

    Parameters:
    v_emp_num (str): The employee number.
    v_client_id (str): The client identifier.

    Returns:
    str: The NI category, defaulting to 'A' if not found.
    """
    print(f"Fetching NI category for employee number: {v_emp_num}, client ID: {v_client_id}")

    # Query MongoDB to fetch NI category
    result = employee_information_collection.find_one(
        {
            "EMPLOYEE_NUMBER": v_emp_num,
            "CLIENT_ID": v_client_id
        },
        {"NI_CATEGORY": 1}
    )

    ni_category = result.get("NI_CATEGORY", "A") if result else 'A'
    print(f"Fetched NI category: {ni_category}")

    return ni_category

def fetch_ytd_value(v_emp_num, balance_category, element_name, v_last_payroll_period, v_client_id):
    """
    Fetches the year-to-date (YTD) value for a given balance category and element name from MongoDB.

    Parameters:
    v_emp_num (str): The employee number.
    balance_category (str): The balance category.
    element_name (str): The element name.
    v_last_payroll_period (str): The last payroll period.
    v_client_id (str): The client identifier.

    Returns:
    float: The year-to-date value, or 0 if not found.
    """
    print(f"Fetching YTD value for employee number: {v_emp_num}, balance category: {balance_category}, element name: {element_name}, last payroll period: {v_last_payroll_period}, client ID: {v_client_id}")

    # Query MongoDB to fetch YTD value
    result = balance_calculation_report_collection.find_one(
        {
            "EMPLOYEE_NUMBER": v_emp_num,
            "BALANCE_CATEGORY": balance_category,
            "ELEMENT_NAME": element_name,
            "PAYROLL_PERIOD": v_last_payroll_period,
            "CLIENT_ID": v_client_id
        },
        {"YEAR_TO_DATE": 1}
    )

    ytd_value = result.get("YEAR_TO_DATE", 0) if result else 0
    print(f"Fetched YTD value: {ytd_value}")

    return ytd_value

# # Test cases for the updated MongoDB functions
# print("Test Case: Fetch NI category")
# ni_category = fetch_ni_category("104", "Bansal Groups_22_03_2024")
# print("Fetched NI category:", ni_category)

# print("\nTest Case: Fetch YTD value")
# ytd_value = fetch_ytd_value("101", "Regular Earnings", "Salary", "3 2024 Calendar Month", "Bansal Groups_22_03_2024")
# print("Fetched YTD value:", ytd_value)

# --------------------------------------------------------------------------------------------------------------------------

def insert_ni_employee_contribution(v_emp_num, v_payroll_period, v_nic_employee, v_ni_employee_ytd, v_client_id):
    """
    Inserts a record for NI Employee Contribution into MongoDB.

    Parameters:
    v_emp_num (str): Employee number.
    v_payroll_period (str): Payroll period.
    v_nic_employee (float): NI employee contribution.
    v_ni_employee_ytd (float): Year-to-date NI employee contribution.
    v_client_id (str): Client ID.
    """
    print(f"Inserting NI employee contribution for employee number: {v_emp_num}, payroll period: {v_payroll_period}, client ID: {v_client_id}")

    # Create a document to insert
    document = {
        "EMPLOYEE_NUMBER": v_emp_num,
        "PAYROLL_PERIOD": v_payroll_period,
        "BALANCE_CATEGORY": "National Insurance Deductions",
        "ELEMENT_NAME": "NI Employee",
        "CLIENT_ID": v_client_id,
        "CURRENT_VALUE": v_nic_employee,
        "YEAR_TO_DATE": v_ni_employee_ytd
    }

    # Insert document into MongoDB collection
    balance_calculation_report_collection.insert_one(document)

    print("NI employee contribution inserted successfully.")

def insert_ni_employer_contribution(v_emp_num, v_payroll_period, v_nic_employer, v_ni_employer_ytd, v_client_id):
    """
    Inserts a record for NI Employer Contribution into MongoDB.

    Parameters:
    v_emp_num (str): Employee number.
    v_payroll_period (str): Payroll period.
    v_nic_employer (float): NI employer contribution.
    v_ni_employer_ytd (float): Year-to-date NI employer contribution.
    v_client_id (str): Client ID.
    """
    print(f"Inserting NI employer contribution for employee number: {v_emp_num}, payroll period: {v_payroll_period}, client ID: {v_client_id}")

    # Create a document to insert
    document = {
        "EMPLOYEE_NUMBER": v_emp_num,
        "PAYROLL_PERIOD": v_payroll_period,
        "BALANCE_CATEGORY": "Employer Taxes",
        "ELEMENT_NAME": "NI Employer",
        "CLIENT_ID": v_client_id,
        "CURRENT_VALUE": v_nic_employer,
        "YEAR_TO_DATE": v_ni_employer_ytd
    }

    # Insert document into MongoDB collection
    balance_calculation_report_collection.insert_one(document)

    print("NI employer contribution inserted successfully.")

# # Test cases for the updated MongoDB functions
# print("Test Case: Insert NI Employee Contribution")
# insert_ni_employee_contribution("E123", "2024-08", 200.50, 1000.75, "client_001")

# print("\nTest Case: Insert NI Employer Contribution")
# insert_ni_employer_contribution("E123", "2024-08", 150.75, 850.25, "client_001")

# --------------------------------------------------------------------------------------------------------------------------

def fetch_tax_deduction_with_pension(v_emp_num, v_payroll_period, v_client_id):
    """
    Fetches the total tax deduction with pension from MongoDB.

    Parameters:
    v_emp_num (str): Employee number.
    v_payroll_period (str): Payroll period.
    v_client_id (str): Client ID.

    Returns:
    float: Total tax deduction with pension.
    """
    print(f"Fetching tax deduction with pension for employee number: {v_emp_num}, payroll period: {v_payroll_period}, client ID: {v_client_id}")

    # Query MongoDB to fetch the sum of CURRENT_VALUE
    pipeline = [
        {
            '$match': {
                'EMPLOYEE_NUMBER': v_emp_num,
                'BALANCE_CATEGORY': {'$in': ['Pre-Statutory Deductions With Pension', 'Pre-Statutory Deductions Without Pension']},
                'PAYROLL_PERIOD': v_payroll_period,
                'CLIENT_ID': v_client_id
            }
        },
        {
            '$group': {
                '_id': None,
                'total': {'$sum': '$CURRENT_VALUE'}
            }
        }
    ]

    result = list(balance_calculation_report_collection.aggregate(pipeline))

    total = result[0]['total'] if result else 0
    print(f"Total tax deduction with pension fetched: {total}")
    return total

def fetch_taxable_gross_till_date(v_emp_num, v_last_payroll_period, v_client_id):
    """
    Fetches the taxable gross till date from MongoDB.

    Parameters:
    v_emp_num (str): Employee number.
    v_last_payroll_period (str): Last payroll period.
    v_client_id (str): Client ID.

    Returns:
    float: Taxable gross till date.
    """
    print(f"Fetching taxable gross till date for employee number: {v_emp_num}, last payroll period: {v_last_payroll_period}, client ID: {v_client_id}")

    # Query MongoDB to fetch YEAR_TO_DATE
    query = {
        'EMPLOYEE_NUMBER': v_emp_num,
        'ELEMENT_NAME': 'Taxable Pay',
        'BALANCE_CATEGORY': 'Tax Deductions',
        'PAYROLL_PERIOD': v_last_payroll_period,
        'CLIENT_ID': v_client_id
    }

    result = balance_calculation_report_collection.find_one(query, {'YEAR_TO_DATE': 1})

    taxable_gross_till_date = result.get('YEAR_TO_DATE', 0) if result else 0
    print(f"Taxable gross till date fetched: {taxable_gross_till_date}")
    return taxable_gross_till_date

# # Test cases for the updated MongoDB functions
# print("Test Case: Fetch Tax Deduction With Pension")
# print("Output:", fetch_tax_deduction_with_pension("E123", "2024-08", "client_001"))

# print("\nTest Case: Fetch Taxable Gross Till Date")
# print("Output:", fetch_taxable_gross_till_date("E123", "2024-07", "client_001"))

# ---------------------------------------------------------------------------------------------------------------------------

def fetch_paye_till_date(v_emp_num, v_last_payroll_period, v_client_id):
    """
    Fetches the PAYE year-to-date value from MongoDB.

    Parameters:
    v_emp_num (str): Employee number.
    v_last_payroll_period (str): Last payroll period.
    v_client_id (str): Client ID.

    Returns:
    float: PAYE year-to-date value.
    """
    print(f"Fetching PAYE till date for employee number: {v_emp_num}, last payroll period: {v_last_payroll_period}, client ID: {v_client_id}")

    # Query MongoDB to fetch YEAR_TO_DATE
    query = {
        'EMPLOYEE_NUMBER': v_emp_num,
        'ELEMENT_NAME': 'PAYE',
        'BALANCE_CATEGORY': 'Tax Deductions',
        'PAYROLL_PERIOD': v_last_payroll_period,
        'CLIENT_ID': v_client_id
    }

    result = balance_calculation_report_collection.find_one(query, {'YEAR_TO_DATE': 1})

    paye_till_date = result.get('YEAR_TO_DATE', 0) if result else 0
    print(f"PAYE till date fetched: {paye_till_date}")
    return paye_till_date

def fetch_tax_code_and_basis(v_emp_num, v_client_id):
    """
    Fetches the tax code and basis for an employee from MongoDB.

    Parameters:
    v_emp_num (str): Employee number.
    v_client_id (str): Client ID.

    Returns:
    tuple: (tax_code, tax_basis)
    """
    print(f"Fetching tax code and basis for employee number: {v_emp_num}, client ID: {v_client_id}")

    # Query MongoDB to fetch TAX_CODE and TAX_BASIS
    query = {
        'EMPLOYEE_NUMBER': v_emp_num,
        'CLIENT_ID': v_client_id
    }

    result = tax_codes_collection.find_one(query, {'TAX_CODE': 1, 'TAX_BASIS': 1})

    tax_code_and_basis = (result.get('TAX_CODE', '1257L'), result.get('TAX_BASIS', 'C')) if result else ('1257L', 'C')
    print(f"Tax code and basis fetched: {tax_code_and_basis}")
    return tax_code_and_basis

# # Test cases for the updated MongoDB functions
# print("Test Case: Fetch PAYE Till Date")
# print("Output:", fetch_paye_till_date("E123", "2024-08", "client_001"))

# print("\nTest Case: Fetch Tax Code and Basis")
# print("Output:", fetch_tax_code_and_basis("E123", "client_001"))

# --------------------------------------------------------------------------------------------------------------------------


def update_ytd_for_april(v_client_id):
    """
    Updates the YEAR_TO_DATE field to be equal to the CURRENT_VALUE field
    for all documents with the specified CLIENT_ID in the MongoDB collection.

    Parameters:
    v_client_id (str): The client ID for which the update should be applied.
    """
    print(f"Updating YEAR_TO_DATE for client ID: {v_client_id}")

    # MongoDB update operation
    update_result = balance_calculation_report_collection.update_many(
        {'CLIENT_ID': v_client_id},
        {'$set': {'YEAR_TO_DATE': '$CURRENT_VALUE'}}
    )

    # Output the result of the update operation
    print(f"Matched documents: {update_result.matched_count}")
    print(f"Modified documents: {update_result.modified_count}")

# # Test case for the updated MongoDB function
# print("Test Case: Update YTD for April")
# update_ytd_for_april("101")

# ---------------------------------------------------------------------------------------------------------------------------


def insert_sickness_data(v_emp_num, v_payroll_period, v_ssp_final_value, v_ssp_ytd, v_client_id):
    """
    Inserts sickness data into the MongoDB collection.

    Parameters:
    v_emp_num (str): Employee number.
    v_payroll_period (str): Payroll period.
    v_ssp_final_value (float): Statutory Sickness Pay final value.
    v_ssp_ytd (float): Year-to-date value for SSP.
    v_client_id (str): Client ID.
    """
    print(f"Inserting sickness data for Employee: {v_emp_num}, Payroll Period: {v_payroll_period}")

    # MongoDB insert operation
    insert_result = balance_calculation_report_collection.insert_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'PAYROLL_PERIOD': v_payroll_period,
        'BALANCE_CATEGORY': 'Absences',
        'ELEMENT_NAME': 'Statutory Sickness',
        'CLIENT_ID': v_client_id,
        'CURRENT_VALUE': v_ssp_final_value,
        'YEAR_TO_DATE': v_ssp_ytd
    })

    # Output the result of the insert operation
    print(f"Inserted document ID: {insert_result.inserted_id}")

def insert_maternity_data(v_emp_num, v_payroll_period, v_smp_final_value, v_smp_ytd, v_client_id):
    """
    Inserts maternity data into the MongoDB collection.

    Parameters:
    v_emp_num (str): Employee number.
    v_payroll_period (str): Payroll period.
    v_smp_final_value (float): Statutory Maternity Pay final value.
    v_smp_ytd (float): Year-to-date value for SMP.
    v_client_id (str): Client ID.
    """
    print(f"Inserting maternity data for Employee: {v_emp_num}, Payroll Period: {v_payroll_period}")

    # MongoDB insert operation
    insert_result = balance_calculation_report_collection.insert_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'PAYROLL_PERIOD': v_payroll_period,
        'BALANCE_CATEGORY': 'Absences',
        'ELEMENT_NAME': 'Statutory Maternity',
        'CLIENT_ID': v_client_id,
        'CURRENT_VALUE': v_smp_final_value,
        'YEAR_TO_DATE': v_smp_ytd
    })

    # Output the result of the insert operation
    print(f"Inserted document ID: {insert_result.inserted_id}")

# # Test cases for the updated MongoDB functions
# print("Test Case: Insert Sickness Data")
# insert_sickness_data("E001", "2024-04", 150.00, 450.00, "client_001")

# print("\nTest Case: Insert Maternity Data")
# insert_maternity_data("E002", "2024-04", 200.00, 600.00, "client_002")


# -----------------------------------------------------------------------------------------------------------------------------------


def insert_paternity_data(v_emp_num, v_payroll_period, v_spp_final_value, v_spp_ytd, v_client_id):
    db = get_mongo_connection()
    document = {
        'EMPLOYEE_NUMBER': v_emp_num,
        'PAYROLL_PERIOD': v_payroll_period,
        'BALANCE_CATEGORY': 'Absences',
        'ELEMENT_NAME': 'Statutory Paternity',
        'CLIENT_ID': v_client_id,
        'CURRENT_VALUE': v_spp_final_value,
        'YEAR_TO_DATE': v_spp_ytd
    }
    balance_calculation_report_collection.insert_one(document)
    print(f"Inserted paternity data for employee {v_emp_num}")

def insert_pension_employee_data(v_emp_num, v_payroll_period, v_pension_employee, v_pension_employee_ytd, v_client_id):
    db = get_mongo_connection()
    document = {
        'EMPLOYEE_NUMBER': v_emp_num,
        'PAYROLL_PERIOD': v_payroll_period,
        'BALANCE_CATEGORY': 'Pre-Statutory Deductions With Pension',
        'ELEMENT_NAME': 'LG Pension Employees Contribution',
        'CLIENT_ID': v_client_id,
        'CURRENT_VALUE': v_pension_employee,
        'YEAR_TO_DATE': v_pension_employee_ytd
    }
    balance_calculation_report_collection.insert_one(document)
    print(f"Inserted pension employee data for employee {v_emp_num}")

def insert_pension_employer_data(v_emp_num, v_payroll_period, v_pension_employer, v_pension_employer_ytd, v_client_id):
    db = get_mongo_connection()
    document = {
        'EMPLOYEE_NUMBER': v_emp_num,
        'PAYROLL_PERIOD': v_payroll_period,
        'BALANCE_CATEGORY': 'Employer Charges',
        'ELEMENT_NAME': 'LG Pension Employers Contribution',
        'CLIENT_ID': v_client_id,
        'CURRENT_VALUE': v_pension_employer,
        'YEAR_TO_DATE': v_pension_employer_ytd
    }
    balance_calculation_report_collection.insert_one(document)
    print(f"Inserted pension employer data for employee {v_emp_num}")

def insert_paye_data(v_emp_num, v_payroll_period, v_paye, v_paye_ytd, v_client_id):
    db = get_mongo_connection()
    document = {
        'EMPLOYEE_NUMBER': v_emp_num,
        'PAYROLL_PERIOD': v_payroll_period,
        'BALANCE_CATEGORY': 'Tax Deductions',
        'ELEMENT_NAME': 'PAYE',
        'CLIENT_ID': v_client_id,
        'CURRENT_VALUE': v_paye,
        'YEAR_TO_DATE': v_paye_ytd
    }
    balance_calculation_report_collection.insert_one(document)
    print(f"Inserted PAYE data for employee {v_emp_num}")

def insert_tax_gross(v_emp_num, v_payroll_period, v_tax_gross, v_tax_gross_ytd, v_client_id):
    db = get_mongo_connection()
    document = {
        'EMPLOYEE_NUMBER': v_emp_num,
        'PAYROLL_PERIOD': v_payroll_period,
        'BALANCE_CATEGORY': 'Tax Deductions',
        'ELEMENT_NAME': 'Taxable Pay',
        'CLIENT_ID': v_client_id,
        'CURRENT_VALUE': v_tax_gross,
        'YEAR_TO_DATE': v_tax_gross_ytd
    }
    balance_calculation_report_collection.insert_one(document)
    print(f"Inserted taxable gross data for employee {v_emp_num}")

# # Define your parameters for the function call
# v_emp_num = 'EMP001'            # Example employee number
# v_payroll_period = '2024-01'    # Example payroll period (format this according to your business logic)
# v_tax_gross = 1500.00           # Example tax gross value
# v_tax_gross_ytd = 4500.00       # Example Year-To-Date tax gross value
# v_client_id = 'client_001'      # Example client ID

# # Call the function to insert the tax gross data into MongoDB
# insert_tax_gross(v_emp_num, v_payroll_period, v_tax_gross, v_tax_gross_ytd, v_client_id)

# ---------------------------------------------------------------------------------------------------------------------------------


def insert_salary_details():
    db = get_mongo_connection()

    # Fetch data from the migration collection
    migration_data = list(migration_data_collection.find({}))

    if not migration_data:
        print("No data found in the migration collection.")
        return

    # Prepare the data for insertion into the salary details collection
    salary_details_data = []
    for record in migration_data:
        salary_record = {
            'EMPLOYEE_NUMBER': record['EMPLOYEE_NUMBER'],
            'SALARY_BASIS_NAME': 'UK_Annual_Salary',
            'ANNUAL_SALARY': record['SALARY_AMOUNT'],
            'SALARY_BASIS_CODE': 'ANNUAL',
            'SALARY_AMOUNT': record['SALARY_AMOUNT'],
            'SALARY_CURRENCY': 'GBP',  # Assuming currency is GBP
            'SALARY_CREATION_DATE': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            'SALARY_LAST_UPDATE': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            'EFFECTIVE_START_DATE': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            'EFFECTIVE_END_DATE': None,  # Assuming no end date is provided
            'HR_STATUS': 'Active',  # Assuming the HR status is 'Active'
            'HOURLY_SALARIED': 'Salaried',  # Assuming a static value for hourly/salaried
            'NORMAL_HOURS': 40,  # Assuming default normal hours
            'CLIENT_ID': record['CLIENT_ID']
        }
        salary_details_data.append(salary_record)

    # Insert data into the salary details collection
    if salary_details_data:
        salary_details_collection.insert_many(salary_details_data)
        print(f"{len(salary_details_data)} records inserted into UK_PS_SALARY_DETAILS.")
    else:
        print("No data prepared for insertion.")


def insert_employee_information():

    # Fetch data from the migration collection
    migration_data = list(migration_data_collection.find({}))

    if not migration_data:
        print("No data found in the migration collection.")
        return

    # Prepare the data for insertion into the employee information collection
    employee_information_data = []
    for record in migration_data:
        employee_record = {
            'EMPLOYEE_NUMBER': record.get('EMPLOYEE_NUMBER'),
            'TITLE': record.get('TITLE'),
            'FIRST_NAME': record.get('FIRST_NAME'),
            'LAST_NAME': record.get('LAST_NAME'),
            'ADDRESS_LINE_1': record.get('ADDRESS_LINE_1'),
            'ADDRESS_LINE_2': record.get('ADDRESS_LINE_2'),
            'ADDRESS_LINE_3': record.get('ADDRESS_LINE_3'),
            'ADDRESS_LINE_4': record.get('ADDRESS_LINE_4'),
            'CITY': record.get('CITY'),
            'POSTAL_CODE': record.get('POSTAL_CODE'),
            'DATE_OF_BIRTH': record.get('DATE_OF_BIRTH'),  # Ensure DATE_OF_BIRTH is in correct format
            'PERSON_GENDER': record.get('PERSON_GENDER'),
            'CLIENT_ID': record.get('CLIENT_ID')
        }
        employee_information_data.append(employee_record)

    # Insert data into the employee information collection
    if employee_information_data:
        employee_information_collection.insert_many(employee_information_data)
        print(f"{len(employee_information_data)} records inserted into UK_PS_EMPLOYEE_INFORMATION.")
    else:
        print("No data prepared for insertion.")


def insert_tax_codes():

    # Fetch data from the migration collection
    migration_data = list(migration_data_collection.find({}))

    if not migration_data:
        print("No data found in the migration collection.")
        return

    # Prepare the data for insertion into the tax codes collection
    tax_codes_data = []
    for record in migration_data:
        tax_record = {
            'EMPLOYEE_NUMBER': record.get('EMPLOYEE_NUMBER'),
            'TAX_CODE': record.get('TAX_CODE', '1257L'),  # Example of a default tax code if none provided
            'TAX_BASIS': record.get('TAX_BASIS', 'C'),   # Example of a default tax basis if none provided
            'CLIENT_ID': record.get('CLIENT_ID')
        }
        tax_codes_data.append(tax_record)

    # Insert data into the tax codes collection
    if tax_codes_data:
        tax_codes_collection.insert_many(tax_codes_data)
        print(f"{len(tax_codes_data)} records inserted into UK_PS_TAX_CODES.")
    else:
        print("No data prepared for insertion.")


def insert_pension_details():

    # Fetch data from the migration collection
    migration_data = list(migration_data_collection.find({}))

    if not migration_data:
        print("No data found in the migration collection.")
        return

    # Prepare the data for insertion into the pension details collection
    pension_data = []
    for record in migration_data:
        pension_record = {
            'EMPLOYEE_NUMBER': record.get('EMPLOYEE_NUMBER'),
            'EMPLOYEE_NAME': f"{record.get('FIRST_NAME', '')} {record.get('LAST_NAME', '')}".strip(),
            'PENSION_SCHEME': 'Basic Pension',  # Default pension scheme
            'TYPE_OF_SCHEME': 'Defined Contribution',  # Default type of scheme
            'EMPLOYEE_CONTRIBUTION': 5.0,  # Default employee contribution percentage
            'EMPLOYEE_AV_CONTRIBUTION': 5.0,  # Default average employee contribution percentage
            'EMPLOYER_CONTRIBUTION': 3.0,  # Default employer contribution percentage
            'CREATION_DATE': datetime.now().strftime('%Y-%m-%d'),  # Current date as creation date
            'LAST_UPDATED_DATE': datetime.now().strftime('%Y-%m-%d'),  # Current date as last updated date
            'CLIENT_ID': record.get('CLIENT_ID')
        }
        pension_data.append(pension_record)

    # Insert data into the pension collection
    if pension_data:
        pension_details_collection.insert_many(pension_data)
        print(f"{len(pension_data)} records inserted into UK_PS_PENSION_DETAILS.")
    else:
        print("No data prepared for insertion.")


def fetch_salary_ytd(v_emp_num, balance_category, element_name, v_last_payroll_period, v_client_id):

    result = balance_calculation_report_collection.find_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'BALANCE_CATEGORY': balance_category,
        'ELEMENT_NAME': element_name,
        'PAYROLL_PERIOD': v_last_payroll_period,
        'CLIENT_ID': v_client_id
    }, {'YEAR_TO_DATE': 1})

    return result.get('YEAR_TO_DATE', 0) if result else 0


def fetch_smp_ytd(v_emp_num, balance_category, element_name, v_last_payroll_period, v_client_id):

    result = balance_calculation_report_collection.find_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'BALANCE_CATEGORY': balance_category,
        'ELEMENT_NAME': element_name,
        'PAYROLL_PERIOD': v_last_payroll_period,
        'CLIENT_ID': v_client_id
    }, {'YEAR_TO_DATE': 1})

    return result.get('YEAR_TO_DATE', 0) if result else 0


def fetch_spp_ytd(v_emp_num, balance_category, element_name, v_last_payroll_period, v_client_id):

    result = balance_calculation_report_collection.find_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'BALANCE_CATEGORY': balance_category,
        'ELEMENT_NAME': element_name,
        'PAYROLL_PERIOD': v_last_payroll_period,
        'CLIENT_ID': v_client_id
    }, {'YEAR_TO_DATE': 1})

    return result.get('YEAR_TO_DATE', 0) if result else 0

