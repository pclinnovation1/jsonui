

from pymongo import MongoClient
from datetime import datetime, timedelta
import re

# Database connection utility
def connect_to_mongodb():
    client = MongoClient('mongodb://localhost:27017')
    return client['mydatabase']
def get_db_connection():
    client = MongoClient('mongodb://localhost:27017')
    return client['mydatabase']

def preprocess_datetime_string(dt_str):
    match = re.match(r'(\d{2})-([A-Za-z]{3})-(\d{2}) (\d{2})\.(\d{2})\.(\d{2})\.(\d{9}) (AM|PM)', dt_str)
    if match:
        day = int(match.group(1))
        month = match.group(2)
        year = int(match.group(3))
        hour = int(match.group(4))
        minute = int(match.group(5))
        second = int(match.group(6))
        microsecond = int(match.group(7)) // 1000  # Convert nanoseconds to microseconds
        meridian = match.group(8)
        
        if meridian == 'PM' and hour != 12:
            hour += 12

        return datetime(year, datetime.strptime(month, "%b").month, day, hour, minute, second, microsecond)
    else:
        return None

def insert_ni_employee_contribution(v_emp_num, v_payroll_period, v_nic_employee, v_ni_employee_ytd, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    document = {
        'EMPLOYEE_NUMBER': v_emp_num,
        'PAYROLL_PERIOD': v_payroll_period,
        'BALANCE_CATEGORY': 'National Insurance Deductions',
        'ELEMENT_NAME': 'NI Employee',
        'CLIENT_ID': v_client_id,
        'CURRENT_VALUE': v_nic_employee,
        'YEAR_TO_DATE': v_ni_employee_ytd
    }
    collection.insert_one(document)

def insert_ni_employer_contribution(v_emp_num, v_payroll_period, v_nic_employer, v_ni_employer_ytd, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    document = {
        'EMPLOYEE_NUMBER': v_emp_num,
        'PAYROLL_PERIOD': v_payroll_period,
        'BALANCE_CATEGORY': 'Employer Taxes',
        'ELEMENT_NAME': 'NI Employer',
        'CLIENT_ID': v_client_id,
        'CURRENT_VALUE': v_nic_employer,
        'YEAR_TO_DATE': v_ni_employer_ytd
    }
    collection.insert_one(document)

def fetch_tax_deduction_with_pension(v_emp_num, v_payroll_period, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
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
    result = list(collection.aggregate(pipeline))
    return result[0]['total'] if result else 0

def fetch_taxable_gross_till_date(v_emp_num, v_last_payroll_period, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    result = collection.find_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'ELEMENT_NAME': 'Taxable Pay',
        'BALANCE_CATEGORY': 'Tax Deductions',
        'PAYROLL_PERIOD': v_last_payroll_period,
        'CLIENT_ID': v_client_id
    }, {'YEAR_TO_DATE': 1})
    return result['YEAR_TO_DATE'] if result else 0

def fetch_paye_till_date(v_emp_num, v_last_payroll_period, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    result = collection.find_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'ELEMENT_NAME': 'PAYE',
        'BALANCE_CATEGORY': 'Tax Deductions',
        'PAYROLL_PERIOD': v_last_payroll_period,
        'CLIENT_ID': v_client_id
    }, {'YEAR_TO_DATE': 1})
    return result['YEAR_TO_DATE'] if result else 0

def fetch_tax_code_and_basis(v_emp_num, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_TAX_CODES']
    result = collection.find_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'CLIENT_ID': v_client_id
    }, {'TAX_CODE': 1, 'TAX_BASIS': 1})
    return (result['TAX_CODE'], result['TAX_BASIS']) if result else ('1257L', 'C')  # Default values

def update_gross_pay(v_emp_num, v_payroll_period, v_gross_pay, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    collection.update_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'PAYROLL_PERIOD': v_payroll_period,
        'CLIENT_ID': v_client_id
    }, {'$set': {'GROSS_PAY': v_gross_pay}})

def update_ytd_for_april(v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    collection.update_many({
        'CLIENT_ID': v_client_id
    }, {'$set': {'YEAR_TO_DATE': '$CURRENT_VALUE'}})

def insert_sickness_data(v_emp_num, v_payroll_period, v_ssp_final_value, v_ssp_ytd, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    document = {
        'EMPLOYEE_NUMBER': v_emp_num,
        'PAYROLL_PERIOD': v_payroll_period,
        'BALANCE_CATEGORY': 'Absences',
        'ELEMENT_NAME': 'Statutory Sickness',
        'CLIENT_ID': v_client_id,
        'CURRENT_VALUE': v_ssp_final_value,
        'YEAR_TO_DATE': v_ssp_ytd
    }
    collection.insert_one(document)

def insert_maternity_data(v_emp_num, v_payroll_period, v_smp_final_value, v_smp_ytd, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    document = {
        'EMPLOYEE_NUMBER': v_emp_num,
        'PAYROLL_PERIOD': v_payroll_period,
        'BALANCE_CATEGORY': 'Absences',
        'ELEMENT_NAME': 'Statutory Maternity',
        'CLIENT_ID': v_client_id,
        'CURRENT_VALUE': v_smp_final_value,
        'YEAR_TO_DATE': v_smp_ytd
    }
    collection.insert_one(document)

def insert_paternity_data(v_emp_num, v_payroll_period, v_spp_final_value, v_spp_ytd, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    document = {
        'EMPLOYEE_NUMBER': v_emp_num,
        'PAYROLL_PERIOD': v_payroll_period,
        'BALANCE_CATEGORY': 'Absences',
        'ELEMENT_NAME': 'Statutory Paternity',
        'CLIENT_ID': v_client_id,
        'CURRENT_VALUE': v_spp_final_value,
        'YEAR_TO_DATE': v_spp_ytd
    }
    collection.insert_one(document)

def insert_pension_employee_data(v_emp_num, v_payroll_period, v_pension_employee, v_pension_employee_ytd, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    document = {
        'EMPLOYEE_NUMBER': v_emp_num,
        'PAYROLL_PERIOD': v_payroll_period,
        'BALANCE_CATEGORY': 'Pre-Statutory Deductions With Pension',
        'ELEMENT_NAME': 'LG Pension Employees Contribution',
        'CLIENT_ID': v_client_id,
        'CURRENT_VALUE': v_pension_employee,
        'YEAR_TO_DATE': v_pension_employee_ytd
    }
    collection.insert_one(document)

def insert_pension_employer_data(v_emp_num, v_payroll_period, v_pension_employer, v_pension_employer_ytd, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    document = {
        'EMPLOYEE_NUMBER': v_emp_num,
        'PAYROLL_PERIOD': v_payroll_period,
        'BALANCE_CATEGORY': 'Employer Charges',
        'ELEMENT_NAME': 'LG Pension Employers Contribution',
        'CLIENT_ID': v_client_id,
        'CURRENT_VALUE': v_pension_employer,
        'YEAR_TO_DATE': v_pension_employer_ytd
    }
    collection.insert_one(document)

def insert_paye_data(v_emp_num, v_payroll_period, v_paye, v_paye_ytd, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    document = {
        'EMPLOYEE_NUMBER': v_emp_num,
        'PAYROLL_PERIOD': v_payroll_period,
        'BALANCE_CATEGORY': 'Tax Deductions',
        'ELEMENT_NAME': 'PAYE',
        'CLIENT_ID': v_client_id,
        'CURRENT_VALUE': v_paye,
        'YEAR_TO_DATE': v_paye_ytd
    }
    collection.insert_one(document)

def insert_tax_gross(v_emp_num, v_payroll_period, v_tax_gross, v_tax_gross_ytd, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    document = {
        'EMPLOYEE_NUMBER': v_emp_num,
        'PAYROLL_PERIOD': v_payroll_period,
        'BALANCE_CATEGORY': 'Tax Deductions',
        'ELEMENT_NAME': 'Taxable Pay',
        'CLIENT_ID': v_client_id,
        'CURRENT_VALUE': v_tax_gross,
        'YEAR_TO_DATE': v_tax_gross_ytd
    }
    collection.insert_one(document)

def insert_salary_details():
    db = connect_to_mongodb()
    migration_collection = db['UK_PS_MIGRATION_DATA_TABLE_1']
    salary_details_collection = db['UK_PS_SALARY_DETAILS']

    documents = []
    for doc in migration_collection.find():
        document = {
            'EMPLOYEE_NUMBER': doc['EMPLOYEE_NUMBER'],
            'SALARY_BASIS_NAME': 'UK_Annual_Salary',
            'ANNUAL_SALARY': doc['SALARY_AMOUNT'],
            'SALARY_BASIS_CODE': 'ANNUAL',
            'SALARY_AMOUNT': doc['SALARY_AMOUNT'],
            'SALARY_CURRENCY': 'GBP',  # Assuming currency is GBP
            'SALARY_CREATION_DATE': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'SALARY_LAST_UPDATE': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'EFFECTIVE_START_DATE': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'EFFECTIVE_END_DATE': None,
            'HR_STATUS': 'Active',
            'HOURLY_SALARIED': 'Salaried',
            'NORMAL_HOURS': 40,
            'CLIENT_ID': doc['CLIENT_ID']
        }
        documents.append(document)

    if documents:
        salary_details_collection.insert_many(documents)
        print(f"{len(documents)} documents inserted into UK_PS_SALARY_DETAILS.")

def insert_employee_information():
    db = connect_to_mongodb()
    migration_collection = db['UK_PS_MIGRATION_DATA_TABLE_1']
    employee_info_collection = db['UK_PS_EMPLOYEE_INFORMATION']

    documents = []
    for doc in migration_collection.find():
        document = {
            'EMPLOYEE_NUMBER': doc['EMPLOYEE_NUMBER'],
            'TITLE': doc['TITLE'],
            'FIRST_NAME': doc['FIRST_NAME'],
            'LAST_NAME': doc['LAST_NAME'],
            'ADDRESS_LINE_1': doc['ADDRESS_LINE_1'],
            'ADDRESS_LINE_2': doc['ADDRESS_LINE_2'],
            'ADDRESS_LINE_3': doc.get('ADDRESS_LINE_3'),
            'ADDRESS_LINE_4': doc.get('ADDRESS_LINE_4'),
            'CITY': doc['CITY'],
            'POSTAL_CODE': doc['POSTAL_CODE'],
            'DATE_OF_BIRTH': doc['DATE_OF_BIRTH'],
            'PERSON_GENDER': doc['PERSON_GENDER'],
            'CLIENT_ID': doc['CLIENT_ID']
        }
        documents.append(document)

    if documents:
        employee_info_collection.insert_many(documents)
        print(f"{len(documents)} documents inserted into UK_PS_EMPLOYEE_INFORMATION.")

def insert_tax_codes():
    db = connect_to_mongodb()
    migration_collection = db['UK_PS_MIGRATION_DATA_TABLE_1']
    tax_codes_collection = db['UK_PS_TAX_CODES']

    documents = []
    for doc in migration_collection.find():
        document = {
            'EMPLOYEE_NUMBER': doc['EMPLOYEE_NUMBER'],
            'TAX_CODE': doc.get('TAX_CODE', '1257L'),  # Example of default or calculated tax code
            'TAX_BASIS': doc.get('TAX_BASIS', 'C'),  # Example of default tax basis
            'CLIENT_ID': doc['CLIENT_ID']
        }
        documents.append(document)

    if documents:
        tax_codes_collection.insert_many(documents)
        print(f"{len(documents)} documents inserted into UK_PS_TAX_CODES.")

def insert_pension_details():
    db = connect_to_mongodb()
    migration_collection = db['UK_PS_MIGRATION_DATA_TABLE_1']
    pension_details_collection = db['UK_PS_PENSION_DETAILS']

    documents = []
    for doc in migration_collection.find():
        document = {
            'EMPLOYEE_NUMBER': doc['EMPLOYEE_NUMBER'],
            'EMPLOYEE_NAME': f"{doc['FIRST_NAME']} {doc['LAST_NAME']}",
            'PENSION_SCHEME': 'Basic Pension',
            'TYPE_OF_SCHEME': 'Defined Contribution',
            'EMPLOYEE_CONTRIBUTION': 5.0,  # Default employee contribution percentage
            'EMPLOYEE_AV_CONTRIBUTION': 5.0,  # Default average employee contribution percentage
            'EMPLOYER_CONTRIBUTION': 3.0,  # Default employer contribution percentage
            'CREATION_DATE': datetime.now().strftime('%Y-%m-%d'),
            'LAST_UPDATED_DATE': datetime.now().strftime('%Y-%m-%d'),
            'CLIENT_ID': doc['CLIENT_ID']
        }
        documents.append(document)

    if documents:
        pension_details_collection.insert_many(documents)
        print(f"{len(documents)} documents inserted into UK_PS_PENSION_DETAILS.")

def fetch_salary_ytd(v_emp_num, balance_category, element_name, v_last_payroll_period, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    result = collection.find_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'BALANCE_CATEGORY': balance_category,
        'ELEMENT_NAME': element_name,
        'PAYROLL_PERIOD': v_last_payroll_period,
        'CLIENT_ID': v_client_id
    }, {'YEAR_TO_DATE': 1})
    return result['YEAR_TO_DATE'] if result else 0

def fetch_smp_ytd(v_emp_num, balance_category, element_name, v_last_payroll_period, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    result = collection.find_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'BALANCE_CATEGORY': balance_category,
        'ELEMENT_NAME': element_name,
        'PAYROLL_PERIOD': v_last_payroll_period,
        'CLIENT_ID': v_client_id
    }, {'YEAR_TO_DATE': 1})
    return result['YEAR_TO_DATE'] if result else 0

def fetch_spp_ytd(v_emp_num, balance_category, element_name, v_last_payroll_period, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    result = collection.find_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'BALANCE_CATEGORY': balance_category,
        'ELEMENT_NAME': element_name,
        'PAYROLL_PERIOD': v_last_payroll_period,
        'CLIENT_ID': v_client_id
    }, {'YEAR_TO_DATE': 1})
    return result['YEAR_TO_DATE'] if result else 0

def fetch_hire_date(client_id, emp_no):
    db = connect_to_mongodb()
    collection = db['UK_PS_MIGRATION_DATA_TABLE_1']
    result = collection.find_one({
        'CLIENT_ID': client_id,
        'EMPLOYEE_NUMBER': emp_no
    }, {'HIRE_DATE': 1})
    if result:
        hire_date = datetime.strptime(result['HIRE_DATE'], '%Y-%m-%d %H:%M:%S')
        return hire_date
    else:
        print("No hire date found")
        return None

def UK_PS_SALARY_RETROACTIVE(p_employee_number, p1_payroll_process_date, p2_previous_payroll_process_date, p5_effective_start_payroll_process_date):
    db = connect_to_mongodb()
    salary_details_collection = db['UK_PS_SALARY_DETAILS']

    l_p1_payroll_process_date = '2023-06-15'  # Format datetime in MongoDB format
    l_p2_previous_payroll_process_date = '2023-05-15'  # Format datetime in MongoDB format

    V_PERIOD = None  # Initialize V_PERIOD

    # Fetch v3_sal_last_update_date
    result = salary_details_collection.find_one({
        'EMPLOYEE_NUMBER': p_employee_number,
        'EFFECTIVE_START_DATE': {'$lte': '2023-06-30'},
        'SALARY_CREATION_DATE': {'$lte': p1_payroll_process_date}
    }, sort=[('EFFECTIVE_START_DATE', -1)], projection={'SALARY_CREATION_DATE': 1})
    v3_sal_last_update_date = result['SALARY_CREATION_DATE'] if result else None

    # Fetch V_ANNUAL_SALARY, V4_EFFECTIVE_START, and V_EFFECTIVE_END
    result = salary_details_collection.find_one({
        'EMPLOYEE_NUMBER': p_employee_number,
        'HOURLY_SALARIED': 'Salaried',
        'HR_STATUS': 'ACTIVE',
        'SALARY_CREATION_DATE': v3_sal_last_update_date
    }, sort=[('EFFECTIVE_START_DATE', 1)], projection={'ANNUAL_SALARY': 1, 'EFFECTIVE_START_DATE': 1, 'EFFECTIVE_END_DATE': 1})
    V_ANNUAL_SALARY = result['ANNUAL_SALARY'] if result else 0
    V4_EFFECTIVE_START = result['EFFECTIVE_START_DATE'] if result else None
    V_EFFECTIVE_END = result['EFFECTIVE_END_DATE'] if result else None

    # Fetch v_sal_second_last_update_date
    result = salary_details_collection.find_one({
        'EMPLOYEE_NUMBER': p_employee_number,
        'EFFECTIVE_START_DATE': {'$lte': '2023-06-30'},
        'SALARY_CREATION_DATE': {'$lte': p1_payroll_process_date}
    }, sort=[('EFFECTIVE_START_DATE', -1)], skip=1, limit=1, projection={'SALARY_CREATION_DATE': 1})
    v_sal_second_last_update_date = result['SALARY_CREATION_DATE'] if result else None

    # Fetch V_ANNUAL_SALARY_BEFORE_V3
    result = salary_details_collection.find_one({
        'EMPLOYEE_NUMBER': p_employee_number,
        'HOURLY_SALARIED': 'Salaried',
        'HR_STATUS': 'ACTIVE',
        'SALARY_CREATION_DATE': v_sal_second_last_update_date
    }, sort=[('EFFECTIVE_START_DATE', 1)], projection={'ANNUAL_SALARY': 1})
    V_ANNUAL_SALARY_BEFORE_V3 = result['ANNUAL_SALARY'] if result else 0

    # Calculate l_p5_effective_start_payroll_process_date if V4_EFFECTIVE_START is not None
    l_p5_effective_start_payroll_process_date = V4_EFFECTIVE_START if V4_EFFECTIVE_START else None

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

def uk_ps_absence_entitlement_days(emp_num, start, end, payroll_process_date, client_id):
    total_days = 0
    db = connect_to_mongodb()
    collection = db['UK_PS_ABSENCE_DETAILS']

    cursor = collection.find({
        'EMPLOYEE_ID': emp_num,
        'LEAVE_TYPE': 'GB Paternity Leave',
        'LAST_UPDATE_DATE': {'$lt': payroll_process_date},
        'CLIENT_ID': client_id
    }, {'LEAVE_START_DATE_TIME': 1, 'LEAVE_END_DATE_TIME': 1})

    for record in cursor:
        leave_start = preprocess_datetime_string(record['LEAVE_START_DATE_TIME'])
        leave_end = preprocess_datetime_string(record['LEAVE_END_DATE_TIME'])

        absence_start = max(leave_start, start)
        absence_end = min(leave_end, end)
        absence_interval = absence_end - absence_start
        absence_duration = absence_interval.days + absence_interval.seconds / (24 * 3600)

        if absence_start > absence_end:
            continue
        elif leave_start.month == leave_end.month:
            total_days += absence_duration
        else:
            if int(absence_duration) == absence_duration:
                total_days += (absence_end - absence_start).days + 1
            else:
                total_days += (absence_end - absence_start).days + absence_duration % 1

    return total_days

def uk_ps_absence_entitlement_days_1(emp_num, start, end, payroll_process_date, client_id):
    total_days = 0
    db = connect_to_mongodb()
    collection = db['UK_PS_ABSENCE_DETAILS']

    if isinstance(start, str):
        start = datetime.strptime(start, '%Y-%m-%d')

    cursor = collection.find({
        'EMPLOYEE_ID': emp_num,
        'LEAVE_TYPE': {'$in': ['Annual Leave']},
        'LAST_UPDATE_DATE': {'$lt': payroll_process_date},
        'CLIENT_ID': client_id
    }, {'LEAVE_START_DATE_TIME': 1, 'LEAVE_END_DATE_TIME': 1})

    for record in cursor:
        leave_start = record['LEAVE_START_DATE_TIME']
        leave_end = record['LEAVE_END_DATE_TIME']

        if isinstance(leave_start, str):
            leave_start = datetime.strptime(leave_start, '%d-%b-%y %I.%M.%S.%f000000 %p')

        if isinstance(leave_end, str):
            leave_end = datetime.strptime(leave_end, '%d-%b-%y %I.%M.%S.%f000000 %p')

        absence_start = max(leave_start, start)
        absence_end = min(leave_end, end)

        if absence_start > absence_end:
            continue

        absence_duration = (absence_end - absence_start).days + 1

        total_days += absence_duration

    return total_days

def fetch_latest_salary_update(emp_num, end_date, payroll_process_date, client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_SALARY_DETAILS']
    result = collection.find_one({
        'EMPLOYEE_NUMBER': emp_num,
        'EFFECTIVE_START_DATE': {'$lte': end_date},
        'SALARY_CREATION_DATE': {'$lte': payroll_process_date},
        'CLIENT_ID': client_id
    }, sort=[('EFFECTIVE_START_DATE', -1)], projection={'SALARY_CREATION_DATE': 1})
    if result and result['SALARY_CREATION_DATE']:
        return datetime.strptime(result['SALARY_CREATION_DATE'], '%Y-%m-%d %H:%M:%S')
    else:
        return None
def fetch_annual_salary(emp_num, salary_creation_date, client_id):
    db = get_db_connection()
    result = db.UK_PS_EMPLOYEE_INFORMATION.find_one(
        {"EMPLOYEE_NUMBER": emp_num, "SALARY_CREATION_DATE": salary_creation_date, "CLIENT_ID": client_id},
        projection={"ANNUAL_SALARY": 1}
    )
    if result:
        return result['ANNUAL_SALARY']
    else:
        return 0

def fetch_annual_salary_1(emp_num, start_date, end_date, client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_SALARY_DETAILS']
    result = collection.find_one({
        'EMPLOYEE_NUMBER': emp_num,
        'HOURLY_SALARIED': 'Salaried',
        'HR_STATUS': 'ACTIVE',
        'EFFECTIVE_START_DATE': {'$lte': end_date},
        'EFFECTIVE_END_DATE': {'$gte': start_date},
        'CLIENT_ID': client_id
    }, sort=[('EFFECTIVE_START_DATE', -1)], projection={'ANNUAL_SALARY': 1, 'EFFECTIVE_START_DATE': 1, 'EFFECTIVE_END_DATE': 1})
    if result:
        return float(result['ANNUAL_SALARY']), result['EFFECTIVE_START_DATE'], result['EFFECTIVE_END_DATE']
    else:
        return 0, None, None

def uk_ps_ytd_salary_deduction(emp_num, start_date, end_date, absence_type, client_id):
    total_deduction = 0

    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    db = connect_to_mongodb()
    collection = db['UK_PS_ABSENCE_DETAILS']

    cursor = collection.find({
        'EMPLOYEE_ID': emp_num,
        'LEAVE_TYPE': absence_type,
        'LEAVE_START_DATE_TIME': {'$lte': end_date},
        'LEAVE_END_DATE_TIME': {'$gte': start_date},
        'CLIENT_ID': client_id
    }, {'LEAVE_START_DATE_TIME': 1, 'LEAVE_END_DATE_TIME': 1})

    for abs_rec in cursor:
        abs_start = max(datetime.strptime(abs_rec['LEAVE_START_DATE_TIME'], '%d-%b-%y %I.%M.%S.%f000000 %p'), start_date)
        abs_end = min(datetime.strptime(abs_rec['LEAVE_END_DATE_TIME'], '%d-%b-%y %I.%M.%S.%f000000 %p'), end_date)

        salary_cursor = db['UK_PS_SALARY_DETAILS'].find({
            'EMPLOYEE_NUMBER': emp_num,
            'EFFECTIVE_START_DATE': {'$lte': abs_end},
            '$or': [{'EFFECTIVE_END_DATE': {'$gte': abs_start}}, {'EFFECTIVE_END_DATE': None}],
            'CLIENT_ID': client_id
        }, sort=[('EFFECTIVE_START_DATE', 1)], projection={'ANNUAL_SALARY': 1, 'EFFECTIVE_START_DATE': 1, 'EFFECTIVE_END_DATE': 1})

        for sal_rec in salary_cursor:
            salary = sal_rec['ANNUAL_SALARY']
            salary_change = max(datetime.strptime(sal_rec['EFFECTIVE_START_DATE'], '%Y-%m-%d %H:%M:%S'), abs_start)
            processed = False

            while salary_change <= abs_end and not processed:
                if 'EFFECTIVE_END_DATE' in sal_rec and isinstance(sal_rec['EFFECTIVE_END_DATE'], datetime):
                    period_deduction = salary / 365 * ((sal_rec['EFFECTIVE_END_DATE'] - salary_change).days + 1)
                else:
                    period_deduction = salary / 365 * ((abs_end - salary_change).days + 1)

                total_deduction += period_deduction

                if 'EFFECTIVE_END_DATE' in sal_rec and isinstance(sal_rec['EFFECTIVE_END_DATE'], datetime) and sal_rec['EFFECTIVE_END_DATE'] < abs_end:
                    salary_change = sal_rec['EFFECTIVE_END_DATE'] + timedelta(days=1)
                    processed = True
                else:
                    break

    return total_deduction

def fetch_dates_from_db(v_payroll_period, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_PAYROLL_PERIODS']
    result = collection.find_one({
        'PERIOD_NAME_MODIFIED': v_payroll_period,
        'CLIENT_ID': v_client_id
    }, {'START_DATE': 1, 'END_DATE': 1, 'PAYROLL_RUN_DATE': 1, 'CUTOFF_DATE': 1, 'MONTH_NUMBER': 1})
    if result:
        dates = [datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S') if date_str else None for date_str in [result['START_DATE'], result['END_DATE'], result['PAYROLL_RUN_DATE'], result['CUTOFF_DATE']]]
        month_number = int(result['MONTH_NUMBER']) if result['MONTH_NUMBER'] is not None else None
        dates.append(month_number)
        return dates
    else:
        raise Exception("No data found")

def fetch_hire_dates_from_db(vemp_num, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_MIGRATION_DATA_TABLE_1']
    result = collection.find_one({
        'EMPLOYEE_NUMBER': vemp_num,
        'CLIENT_ID': v_client_id
    }, {'hire_date': 1})
    return result['hire_date'] if result else None

def connect_to_mongodb():
    client = MongoClient('mongodb://localhost:27017/')
    return client['my_database']

def fetch_last_payroll_period(v_start_date, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_PAYROLL_PERIODS']
    v_start_date = datetime.strptime(v_start_date, '%Y-%m-%d %H:%M:%S')
    previous_month_end = v_start_date - timedelta(days=1)
    query = {'END_DATE': previous_month_end, 'CLIENT_ID': v_client_id}
    result = collection.find_one(query, {'PERIOD_NAME_MODIFIED': 1})
    return result['PERIOD_NAME_MODIFIED'] if result else None

def fetch_salary_creation_date(emp_num, end_date, process_date, client_id):
    db = get_db_connection()
    result = db.UK_PS_EMPLOYEE_INFORMATION.find_one(
        {"EMPLOYEE_NUMBER": emp_num, "CLIENT_ID": client_id},
        sort=[("SALARY_CREATION_DATE", -1)]
    )
    if result:
        return result['SALARY_CREATION_DATE']
    else:
        return None

def fetch_annual_salary(v_emp_num, v_sal_last_update_date, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_SALARY_DETAILS']
    result = collection.find_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'HR_STATUS': 'Active',
        'SALARY_CREATION_DATE': v_sal_last_update_date,
        'CLIENT_ID': v_client_id
    }, sort=[('EFFECTIVE_START_DATE', -1)], projection={'ANNUAL_SALARY': 1})
    return result['ANNUAL_SALARY'] if result else 0

def fetch_maternity_leave_dates(emp_num, client_id):
    db = get_db_connection()
    results = db.UK_PS_ABSENCE_INFORMATION.find(
        {"EMPLOYEE_NUMBER": emp_num, "CLIENT_ID": client_id, "ABSENCE_TYPE": "Maternity Leave"},
        projection={"START_DATE": 1, "END_DATE": 1}
    )
    return list(results)

def fetch_previous_maternity_ytd(v_emp_num, v_last_payroll_period, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    result = collection.find_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'BALANCE_CATEGORY': 'Absences',
        'ELEMENT_NAME': 'Statutory Maternity',
        'PAYROLL_PERIOD': v_last_payroll_period,
        'CLIENT_ID': v_client_id
    }, {'YEAR_TO_DATE': 1})
    return result['YEAR_TO_DATE'] if result else 0

def fetch_paternity_leave_dates(v_emp_num, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_ABSENCE_DETAILS']
    cursor = collection.find({
        'EMPLOYEE_ID': v_emp_num,
        'LEAVE_TYPE': 'GB Paternity Leave',
        'CLIENT_ID': v_client_id
    }, {'LEAVE_START_DATE_TIME': 1, 'LEAVE_END_DATE_TIME': 1})
    return [(record['LEAVE_START_DATE_TIME'], record['LEAVE_END_DATE_TIME']) for record in cursor]

def fetch_sickness_leave_dates(v_emp_num, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_ABSENCE_DETAILS']
    cursor = collection.find({
        'EMPLOYEE_ID': v_emp_num,
        'LEAVE_TYPE': 'GB2 Sickness',
        'CLIENT_ID': v_client_id
    }, {'LEAVE_START_DATE_TIME': 1, 'LEAVE_END_DATE_TIME': 1})
    return [(record['LEAVE_START_DATE_TIME'], record['LEAVE_END_DATE_TIME']) for record in cursor]

def fetch_absence_entitlement_retro(v_emp_num, v_payroll_period, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    result = collection.find_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'BALANCE_CATEGORY': 'Absences',
        'ELEMENT_NAME': 'Annual Leaves Days Entitlement Retroactive',
        'CLIENT_ID': v_client_id,
        'PAYROLL_PERIOD': v_payroll_period
    }, {'CURRENT_VALUE': 1})
    return result['CURRENT_VALUE'] if result else 0

def fetch_absence_entitlement_retro_ytd(v_emp_num, v_payroll_period, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    result = collection.find_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'BALANCE_CATEGORY': 'Absences',
        'ELEMENT_NAME': 'Annual Leaves Days Entitlement Retroactive',
        'CLIENT_ID': v_client_id,
        'PAYROLL_PERIOD': v_payroll_period
    }, {'YEAR_TO_DATE': 1})
    return result['YEAR_TO_DATE'] if result else 0

def fetch_salary_ytd_previous_period(v_emp_num, v_last_payroll_period, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    result = collection.find_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'BALANCE_CATEGORY': 'Regular Earnings',
        'ELEMENT_NAME': 'Salary',
        'CLIENT_ID': v_client_id,
        'PAYROLL_PERIOD': v_last_payroll_period
    }, {'YEAR_TO_DATE': 1})
    return result['YEAR_TO_DATE'] if result else 0

def fetch_gross_pay(v_emp_num, v_payroll_period, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    pipeline = [
        {
            '$match': {
                'EMPLOYEE_NUMBER': v_emp_num,
                'BALANCE_CATEGORY': {'$in': ['Regular Earnings', 'Irregular Earnings', 'Absences']},
                'ELEMENT_NAME': {'$nin': ['Occupational Sickness Retroactive', 'Statutory Sickness', 'Statutory Sickness Retroactive', 'TRG Sickness Occupational Plan Entitlement Payment', 'Occupational Maternity', 'Occupational Maternity Retroactive']},
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
    result = list(collection.aggregate(pipeline))
    return result[0]['total'] if result else 0

def fetch_pension_contribution(v_emp_num, v_payroll_period, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    pipeline = [
        {
            '$match': {
                'EMPLOYEE_NUMBER': v_emp_num,
                'BALANCE_CATEGORY': {'$in': ['Regular Earnings', 'Absences']},
                'ELEMENT_NAME': {'$nin': ['Occupational Sickness Retroactive', 'TRG Sickness Occupational Plan Entitlement Payment', 'Annual Leaves Days Final Disbursement Payment', 'Annual Leaves Days Final Disbursement Retroactive', 'Annual Leaves Hourly Final Disbursement Payment', 'Annual Leaves Hourly Final Disbursement Retroactive', 'Occupational Maternity', 'Occupational Maternity Retroactive', 'Statutory Paternity Retroactive', 'Statutory Sickness', 'Statutory Sickness Retroactive']},
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
    result = list(collection.aggregate(pipeline))
    return result[0]['total'] if result else 0

def fetch_pension_details(v_emp_num, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_PENSION_DETAILS']
    result = collection.find_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'CLIENT_ID': v_client_id
    }, {'EMPLOYER_CONTRIBUTION': 1, 'EMPLOYEE_CONTRIBUTION': 1})
    return (result['EMPLOYER_CONTRIBUTION'], result['EMPLOYEE_CONTRIBUTION']) if result else (0, 0)

def fetch_pension_ytd(v_emp_num, balance_category, element_name, v_last_payroll_period, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    result = collection.find_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'BALANCE_CATEGORY': balance_category,
        'ELEMENT_NAME': element_name,
        'PAYROLL_PERIOD': v_last_payroll_period,
        'CLIENT_ID': v_client_id
    }, {'YEAR_TO_DATE': 1})
    return result['YEAR_TO_DATE'] if result else 0

def fetch_pre_statutory_deduction(v_emp_num, v_payroll_period, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    pipeline = [
        {
            '$match': {
                'EMPLOYEE_NUMBER': v_emp_num,
                'BALANCE_CATEGORY': 'Pre-Statutory Deductions Without Pension',
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
    result = list(collection.aggregate(pipeline))
    return result[0]['total'] if result else 0

def fetch_niable_gross_till_date(v_emp_num, v_last_payroll_period, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    result = collection.find_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'ELEMENT_NAME': 'NI_GROSS',
        'BALANCE_CATEGORY': 'National Insurance Deductions',
        'PAYROLL_PERIOD': v_last_payroll_period,
        'CLIENT_ID': v_client_id
    }, {'YEAR_TO_DATE': 1})
    return result['YEAR_TO_DATE'] if result else 0

def fetch_ni_category(v_emp_num, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_EMPLOYEE_INFORMATION']
    result = collection.find_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'CLIENT_ID': v_client_id
    }, {'NI_CATEGORY': 1})
    return result['NI_CATEGORY'] if result else 'A'

def fetch_ytd_value(v_emp_num, balance_category, element_name, v_last_payroll_period, v_client_id):
    db = connect_to_mongodb()
    collection = db['UK_PS_BALANCE_CALCULATION_REPORT']
    result = collection.find_one({
        'EMPLOYEE_NUMBER': v_emp_num,
        'BALANCE_CATEGORY': balance_category,
        'ELEMENT_NAME': element_name,
        'PAYROLL_PERIOD': v_last_payroll_period,
        'CLIENT_ID': v_client_id
    }, {'YEAR_TO_DATE': 1})
    return result['YEAR_TO_DATE'] if result else 0

