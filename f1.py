import sqlite3
from datetime import datetime

# Database connection utility
def get_db_connection(db_path='mydatabase.db'):
    return sqlite3.connect(db_path)


from datetime import datetime, timedelta
import re
import math
import numpy as np
from dateutil import parser

from f2 import fetch_latest_salary_update,fetch_annual_salary_1,fetch_annual_salary,uk_ps_absence_entitlement_days_1,uk_ps_absence_entitlement_days

import sqlite3
from datetime import datetime

# Database connection utility
def get_db_connection(db_path='mydatabase.db'):
    return sqlite3.connect(db_path)


from datetime import datetime, timedelta
import re
import math
import numpy as np
from dateutil import parser

# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------


import json
from datetime import timedelta, datetime

def load_config(file_path='Code_wrap/f1.json'):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

config = load_config()
def uk_ps_add_working_days(start_date, num_workdays):
    
    result_date = start_date
    counter = 0
    weekend_days = config['weekend_days']

    while counter < num_workdays:
        result_date += timedelta(days=1)  # Increment the date by one day

        # Check if the resulting date is a workday (based on config)
        while result_date.weekday() in weekend_days:
            result_date += timedelta(days=1)  # If it's a weekend, move to the next day

        counter += 1  # Increment the counter for each workday

    return result_date



# ------------------------------------------------------------------------------------------

def calculate_cost_to_employer(gross_pay, nic_tax_employer, pension_contribution_employer):
    cost_to_employer = gross_pay + nic_tax_employer + pension_contribution_employer
    return cost_to_employer
    


def calculate_net_income(gross_pay, nic_tax_employee, tax_normal, student_loan_repayment):
    net_income = gross_pay - nic_tax_employee - tax_normal - student_loan_repayment
    return net_income
    

def get_employee_config(nic_category):
    for key, value in config['nic_tax_employee'].items():
        if nic_category in value['categories']:
            return value
    return None

def get_employer_config(nic_category):
    for key, value in config['nic_tax_employer'].items():
        if nic_category in value['categories']:
            return value
    return None

def calculate_nic_tax_employee(gross_pay, nic_category='A'):
    tax_amount = 0
    cfg = get_employee_config(nic_category)

    if cfg is None:
        return tax_amount

    if 'threshold1' in cfg:
        if gross_pay <= cfg['threshold1']:
            tax_amount = cfg['rate1']
        elif gross_pay <= cfg['threshold2']:
            tax_amount = cfg['rate2'] * (gross_pay - cfg['threshold1'])
        else:
            tax_amount = (cfg['threshold2'] - cfg['threshold1']) * cfg['rate2'] + cfg['rate3'] * (gross_pay - cfg['threshold2'])
    else:
        tax_amount = cfg['rate']

    return tax_amount

def calculate_nic_tax_employee_2024(gross_pay, nic_category='A'):
    return calculate_nic_tax_employee(gross_pay, nic_category)

def calculate_nic_tax_employer(gross_pay, nic_category='A'):
    tax_amount = 0
    cfg = get_employer_config(nic_category)

    if cfg is None:
        return tax_amount

    if gross_pay > cfg['threshold']:
        tax_amount = cfg['rate'] * (gross_pay - cfg['threshold'])

    return tax_amount



def calculate_nic_tax_employer_2024(gross_pay, nic_category='A'):
    return calculate_nic_tax_employer(gross_pay, nic_category)



def calculate_pension_contribution_employee(gross_pay, employee_pension_contribution=0.05, minimum_limit=0, maximum_limit=0):
    if config:
        employee_config = config['pension']['employee']
        employee_pension_contribution = employee_config['pension_contribution_rate']
        minimum_limit = employee_config['minimum_limit']
        maximum_limit = employee_config['maximum_limit']
    
    pension_contribution = 0

    if gross_pay <= minimum_limit:
        pension_contribution = 0
    elif minimum_limit < gross_pay <= maximum_limit or maximum_limit == 0:
        pension_contribution = employee_pension_contribution * (gross_pay - minimum_limit)
    else:
        if maximum_limit != 0:
            pension_contribution = employee_pension_contribution * (maximum_limit - minimum_limit)

    return pension_contribution

def calculate_pension_contribution_employer(gross_pay, employer_pension_contribution=0.03, minimum_limit=0, maximum_limit=0):
    if config:
        employer_config = config['pension']['employer']
        employer_pension_contribution = employer_config['pension_contribution_rate']
        minimum_limit = employer_config['minimum_limit']
        maximum_limit = employer_config['maximum_limit']
    
    pension_contribution = 0

    if gross_pay <= minimum_limit:
        pension_contribution = 0
    elif minimum_limit < gross_pay <= maximum_limit or maximum_limit == 0:
        pension_contribution = employer_pension_contribution * (gross_pay - minimum_limit)
    else:
        if maximum_limit != 0:
            pension_contribution = employer_pension_contribution * (maximum_limit - minimum_limit)

    return pension_contribution







def calculate_student_loan_repayment(gross_pay, student_loan_plan_type):
    thresholds = config['student_loan']['thresholds']
    rates = config['student_loan']['rates']
    
    repayment_amount = 0

    if student_loan_plan_type in thresholds and gross_pay > thresholds[student_loan_plan_type]:
        repayment_amount = (gross_pay - thresholds[student_loan_plan_type]) * rates[student_loan_plan_type]

    return repayment_amount



def calculate_take_home(net_pay, pension_contribution_employee):
    net_income_after_pension = net_pay - pension_contribution_employee
    return net_income_after_pension
    
    

def calculate_tax_normal(gross_pay, pension_contribution_employee):
    adjusted_pay = gross_pay - pension_contribution_employee
    slabs = config['tax_normal']['slabs']
    
    tax_amount = 0
    previous_threshold = 0

    for slab in slabs:
        threshold = float('inf') if slab['threshold'] == 'inf' else slab['threshold']
        rate = slab['rate']
        if adjusted_pay <= threshold:
            tax_amount += rate * (adjusted_pay - previous_threshold)
            break
        else:
            tax_amount += rate * (threshold - previous_threshold)
        previous_threshold = threshold

    return tax_amount

def calculate_tax_based_on_thresholds(grossable_income, initial_tax, thresholds):
    tax = initial_tax
    for threshold, rate in thresholds:
        if threshold == 'inf':
            threshold = float('inf')
        if grossable_income > threshold:
            tax += (grossable_income - threshold) * rate
            grossable_income = threshold
    return tax

def calculate_tax_normal_with_codes5(tax_code, taxable_gross, pension_employee):
    tax_number = 0

    # Extract numeric part from the tax code
    numeric_part_match = re.search(r'\d+', tax_code)
    numeric_part = int(numeric_part_match.group()) if numeric_part_match else 0
    grossable_income = taxable_gross - math.ceil((numeric_part * 10) / 12)

    slabs = config['tax_normal_with_codes'].get(tax_code[0], [])

    if slabs:
        tax_number = calculate_tax_based_on_thresholds(grossable_income, 0, [(float('inf') if slab['threshold'] == 'inf' else slab['threshold'], slab['rate']) for slab in slabs])
    elif tax_code in config['special_tax_codes']:
        rate = config['special_tax_codes'][tax_code]
        tax_number = rate * taxable_gross
    elif 'L' in tax_code:
        slabs = config['tax_normal_with_codes']['L']
        tax_number = calculate_tax_based_on_thresholds(grossable_income, 0, [(float('inf') if slab['threshold'] == 'inf' else slab['threshold'], slab['rate']) for slab in slabs])
    elif 'K' in tax_code:
        rate = config['special_tax_codes']['K']
        tax_number = rate * (taxable_gross + math.ceil((numeric_part * 10) / 12))

    return tax_number

def calculate_tax_normal_with_codes8(tax_code, taxable_gross, taxable_gross_till_date, paye_till_date, month_number):
    if taxable_gross is None or taxable_gross_till_date is None or month_number is None:
        raise ValueError("One or more input parameters are None")

    tax_number = 0

    # Extract numeric part from the tax code
    numeric_part_match = re.search(r'\d+', tax_code)
    numeric_part = int(numeric_part_match.group()) if numeric_part_match else 0

    if tax_code.startswith('S'):
        grossable_income = taxable_gross - math.ceil((numeric_part * 10) / 12)
        tax_number = calculate_tax_based_on_thresholds(grossable_income, 0, [
            (float('inf') if slab['threshold'] == 'inf' else slab['threshold'], slab['rate']) for slab in config['monthly_thresholds']['S']
        ])

    elif 'L' in tax_code or 'T' in tax_code or 'M' in tax_code or 'N' in tax_code:
        grossable_income = taxable_gross + taxable_gross_till_date - month_number * (math.ceil((numeric_part * 10) / 12) + 0.76)
        general_thresholds = []
        for slab in config['monthly_thresholds']['general']:
            if 'base_threshold' in slab and 'subtraction_value' in slab:
                threshold = month_number * (slab['base_threshold'] - slab['subtraction_value'])
            else:
                threshold = slab['threshold']
            general_thresholds.append((threshold if threshold != 'inf' else float('inf'), slab['rate']))
        tax_number = calculate_tax_based_on_thresholds(grossable_income, 0, general_thresholds)
        tax_number -= paye_till_date

    elif tax_code in config['special_tax_codes']:
        rate = config['special_tax_codes'][tax_code]
        tax_number = rate * taxable_gross

    return tax_number

def calculate_tax_not_normal(gross_pay, pension_contribution_employee, config, min_slab=0):
    adjusted_pay = gross_pay - pension_contribution_employee
    slabs = config['tax_not_normal']['slabs']
    
    tax_amount = 0
    previous_threshold = min_slab

    for slab in slabs:
        threshold = float('inf') if slab['threshold'] == 'inf' else slab['threshold']
        rate = slab['rate']
        if adjusted_pay <= threshold:
            tax_amount += rate * (adjusted_pay - previous_threshold)
            break
        else:
            tax_amount += rate * (threshold - previous_threshold)
        previous_threshold = threshold

    return tax_amount




def uk_ps_networkdays(start_date, end_date):
    # Ensure the input dates are in 'YYYY-MM-DD' format or use the datetime library to parse different formats.
    # Calculate the number of business days between the two dates
    network_days = np.busday_count(start_date, end_date)
    return network_days 


def uk_ps_rp_sal_deduction(leave_start_date, leave_end_date, salary, period_start_date, period_end_date, config):
    # Ensure dates are datetime objects
    if not all(isinstance(date, datetime) for date in [leave_start_date, leave_end_date, period_start_date, period_end_date]):
        raise ValueError("All date inputs must be datetime objects")

    # Ensure the leave dates and period dates are logical
    if leave_start_date > leave_end_date:
        raise ValueError("Leave start date cannot be after leave end date")
    if period_start_date > period_end_date:
        raise ValueError("Period start date cannot be after period end date")

    # Calculate total days in the pay period (can be overridden by config)
    total_days = config.get("salary_period", {}).get("total_days_in_period", (period_end_date - period_start_date).days + 1)

    # Calculate daily salary
    daily_salary = salary / total_days

    # Calculate the number of absence days within the pay period
    absence_start = max(leave_start_date, period_start_date)
    absence_end = min(leave_end_date, period_end_date)
    absence_days = (absence_end - absence_start).days + 1

    # Ensure absence days are not negative
    absence_days = max(absence_days, 0)

    # Calculate the deduction
    deduction = absence_days * daily_salary

    return deduction


def UK_PS_SAP_SMP_FINAL_NEW(p_gross_pay, p_total_weeks_till_now, p_month_weeks):
    thresholds = config["UK_PS_SAP_SMP_FINAL_NEW"]["thresholds"]
    factors = config["UK_PS_SAP_SMP_FINAL_NEW"]["calculation_factors"]
    
    standard_rate = thresholds["standard_rate_2019"]
    weeks_threshold = thresholds["weeks_threshold"]
    gross_pay_factor = factors["gross_pay_multiplier"]
    weeks_in_year = factors["weeks_in_year"]
    months_in_year = factors["months_in_year"]
    
    v_result = None
    weekly_pay = gross_pay_factor * p_gross_pay * months_in_year / weeks_in_year

    if p_total_weeks_till_now == 0:
        if (p_total_weeks_till_now + p_month_weeks) <= weeks_threshold:
            v_result = p_month_weeks * weekly_pay
        else:
            if weekly_pay >= standard_rate:
                v_result = standard_rate * (p_month_weeks + p_total_weeks_till_now - weeks_threshold) + (weeks_threshold - p_total_weeks_till_now) * weekly_pay
            else:
                v_result = weekly_pay * p_month_weeks
    else:
        if p_total_weeks_till_now <= weeks_threshold:
            if (p_total_weeks_till_now + p_month_weeks) <= weeks_threshold:
                v_result = p_month_weeks * weekly_pay
            else:
                if weekly_pay >= standard_rate:
                    v_result = standard_rate * (p_month_weeks + p_total_weeks_till_now - weeks_threshold) + (weeks_threshold - p_total_weeks_till_now) * weekly_pay
                else:
                    v_result = weekly_pay * p_month_weeks
        else:
            if weekly_pay >= standard_rate:
                v_result = standard_rate * p_month_weeks
            else:
                v_result = weekly_pay * p_month_weeks

    return v_result

def UK_PS_SAP_SMP_FINAL_NEW_2024(p_gross_pay, p_total_weeks_till_now, p_month_weeks):
    thresholds = config["UK_PS_SAP_SMP_FINAL_NEW"]["thresholds"]
    factors = config["UK_PS_SAP_SMP_FINAL_NEW"]["calculation_factors"]
    
    standard_rate = thresholds["standard_rate_2024"]
    weeks_threshold = thresholds["weeks_threshold"]
    gross_pay_factor = factors["gross_pay_multiplier"]
    weeks_in_year = factors["weeks_in_year"]
    months_in_year = factors["months_in_year"]
    
    v_result = None
    weekly_pay = gross_pay_factor * p_gross_pay * months_in_year / weeks_in_year

    if p_total_weeks_till_now == 0:
        if (p_total_weeks_till_now + p_month_weeks) <= weeks_threshold:
            v_result = p_month_weeks * weekly_pay
        else:
            if weekly_pay >= standard_rate:
                v_result = standard_rate * (p_month_weeks + p_total_weeks_till_now - weeks_threshold) + (weeks_threshold - p_total_weeks_till_now) * weekly_pay
            else:
                v_result = weekly_pay * p_month_weeks
    else:
        if p_total_weeks_till_now <= weeks_threshold:
            if (p_total_weeks_till_now + p_month_weeks) <= weeks_threshold:
                v_result = p_month_weeks * weekly_pay
            else:
                if weekly_pay >= standard_rate:
                    v_result = standard_rate * (p_month_weeks + p_total_weeks_till_now - weeks_threshold) + (weeks_threshold - p_total_weeks_till_now) * weekly_pay
                else:
                    v_result = weekly_pay * p_month_weeks
        else:
            if weekly_pay >= standard_rate:
                v_result = standard_rate * p_month_weeks
            else:
                v_result = weekly_pay * p_month_weeks

    return v_result

def UK_PS_SAP_SMP_MONTH_DAYS_NEW(p_start_date, p_end_date, p_sap_start_date, p_previous_month_end, p_sap_end_date):
    # Convert string inputs to datetime objects if needed
    if isinstance(p_sap_start_date, str):
        p_sap_start_date = datetime.strptime(p_sap_start_date, '%d-%b-%y %I.%M.%S.%f000000 %p')
    if isinstance(p_previous_month_end, str):
        p_previous_month_end = datetime.strptime(p_previous_month_end, '%d-%b-%y %I.%M.%S.%f000000 %p')
    if isinstance(p_sap_end_date, str):
        p_sap_end_date = datetime.strptime(p_sap_end_date, '%d-%b-%y %I.%M.%S.%f000000 %p')

    v_result = None

    if p_sap_start_date.month == p_end_date.month:
        v_result = (p_end_date - p_sap_start_date).days + 1
    elif p_start_date.month == p_sap_end_date.month:
        v_result = (p_sap_end_date - p_start_date).days + 1
    else:
        v_result = ((p_end_date - p_sap_start_date).days + 1) - ((p_previous_month_end - p_sap_start_date).days + 1)

    return v_result

def UK_PS_SAP_SMP_MONTH_WEEKS_NEW(start_date, end_date, sap_start_date, sap_end_date, month_days):
    # Convert string inputs to datetime objects if needed
    if isinstance(sap_start_date, str):
        sap_start_date = datetime.strptime(sap_start_date, '%d-%b-%y %I.%M.%S.%f000000 %p')
    if isinstance(sap_end_date, str):
        sap_end_date = datetime.strptime(sap_end_date, '%d-%b-%y %I.%M.%S.%f000000 %p')

    if start_date <= sap_end_date and end_date >= sap_start_date:
        result = month_days / 7
    else:
        result = 0
    
    return result



def UK_PS_SAP_SMP_WEEKS_TLL_NOW(start_date, end_date, sap_start_date, sap_end_date, previous_month_end):
    days = 0

    # Convert any string inputs to datetime objects if needed
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    if isinstance(sap_start_date, str):
        # Adjust the format string to match the actual format of sap_start_date
        sap_start_date = datetime.strptime(sap_start_date, '%d-%b-%y %I.%M.%S.%f000000 %p')
    if isinstance(sap_end_date, str):
        # Adjust the format string to match the actual format of sap_end_date
        sap_end_date = datetime.strptime(sap_end_date, '%d-%b-%y %I.%M.%S.%f000000 %p')
    if isinstance(previous_month_end, str):
        previous_month_end = datetime.strptime(previous_month_end, '%Y-%m-%d')

    if start_date.month == sap_start_date.month:
        days = 0
    elif start_date.month == sap_end_date.month:
        days = (previous_month_end - sap_start_date).days // 7
    elif start_date >= sap_start_date and end_date <= sap_end_date:
        days = (previous_month_end - sap_start_date).days // 7

    return days



def UK_PS_SPP_FINAL(gross_pay, month_weeks):
    thresholds = config["UK_PS_SPP_FINAL"]["thresholds"]
    factors = config["UK_PS_SPP_FINAL"]["calculation_factors"]

    standard_rate = thresholds["standard_rate"]
    gross_pay_factor = factors["gross_pay_multiplier"]
    weeks_in_year = factors["weeks_in_year"]
    months_in_year = factors["months_in_year"]
    
    weekly_pay = gross_pay_factor * gross_pay * months_in_year / weeks_in_year
    
    if weekly_pay > standard_rate:
        result = month_weeks * standard_rate
    else:
        result = weekly_pay * month_weeks

    return result

def UK_PS_SPP_FINAL_NEW(gross_pay, month_weeks):
    return UK_PS_SPP_FINAL(gross_pay, month_weeks)

def UK_PS_SPP_FINAL_NEW_2024(gross_pay, month_weeks):
    thresholds = config["UK_PS_SPP_FINAL"]["thresholds"]
    factors = config["UK_PS_SPP_FINAL"]["calculation_factors"]

    standard_rate = thresholds["new_standard_rate_2024"]
    gross_pay_factor = factors["gross_pay_multiplier"]
    weeks_in_year = factors["weeks_in_year"]
    months_in_year = factors["months_in_year"]
    
    weekly_pay = gross_pay_factor * gross_pay * months_in_year / weeks_in_year
    
    if weekly_pay > standard_rate:
        result = month_weeks * standard_rate
    else:
        result = weekly_pay * month_weeks

    return result

def parse_date(date_str):
    try:
        return parser.parse(date_str) if isinstance(date_str, str) else date_str
    except ValueError as e:
        print(f"Error parsing date: {e}, input date string: {date_str}")
        return None

def UK_PS_SPP_MONTH_DAYS(start_date, end_date, spp_start_date, spp_end_date, previous_month_end, total_weeks):
    start_date = parse_date(start_date)
    end_date = parse_date(end_date)
    spp_start_date = parse_date(spp_start_date)
    spp_end_date = parse_date(spp_end_date)
    previous_month_end = parse_date(previous_month_end)

    if any(d is None for d in [start_date, end_date, spp_start_date, spp_end_date, previous_month_end]):
        return 0

    if spp_start_date.month == spp_end_date.month:
        result = 7 * total_weeks
    elif spp_start_date.month == start_date.month:
        result = (end_date - spp_start_date).days + 1
    elif spp_start_date.month == spp_end_date.month:
        result = (spp_end_date - spp_start_date).days - (previous_month_end - spp_start_date).days + (previous_month_end - spp_start_date).days - 7 * ((previous_month_end - spp_start_date).days // 7)
    else:
        result = (end_date - spp_start_date).days - (previous_month_end - spp_start_date).days + (previous_month_end - spp_start_date).days - 7 * ((previous_month_end - spp_start_date).days // 7)
    
    return result

def UK_PS_SPP_MONTH_DAYS_NEW(p_start_date, p_end_date, p_spp_start_date, p_previous_month_end, p_spp_end_date):
    p_start_date = parse_date(p_start_date)
    p_end_date = parse_date(p_end_date)
    p_spp_start_date = parse_date(p_spp_start_date)
    p_previous_month_end = parse_date(p_previous_month_end)
    p_spp_end_date = parse_date(p_spp_end_date)

    if any(d is None for d in [p_start_date, p_end_date, p_spp_start_date, p_previous_month_end, p_spp_end_date]):
        return 0

    if p_spp_start_date.month == p_spp_end_date.month:
        v_result = (p_spp_end_date - p_spp_start_date).days + 1
    elif p_spp_start_date.month == p_start_date.month:
        v_result = (p_end_date - p_spp_start_date).days + 1
    elif p_start_date.month == p_spp_end_date.month:
        v_result = (p_spp_end_date - p_start_date).days + 1
    else:
        v_result = (p_end_date - p_start_date).days + 1

    return v_result

def parse_date_1(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d') if isinstance(date_str, str) else date_str
    except ValueError:
        print(f"Error parsing date: {date_str}")
        return None

def UK_PS_SPP_MONTH_WEEKS_NEW(start_date, end_date, spp_start_date, spp_end_date, month_days):
    start_date = parse_date_1(start_date)
    end_date = parse_date_1(end_date)
    spp_start_date = parse_date_1(spp_start_date)
    spp_end_date = parse_date_1(spp_end_date)

    if any(d is None for d in [start_date, end_date, spp_start_date, spp_end_date]):
        print("One or more dates could not be parsed.")
        return 0

    if start_date <= spp_end_date and end_date >= spp_start_date:
        result = month_days / 7
    else:
        result = 0

    return result

def UK_PS_SPP_WEEKS_TLL_NOW_NEW(start_date, end_date, spp_start_date, spp_end_date, previous_month_end):
    start_date = parse_date(start_date)
    end_date = parse_date(end_date)
    spp_start_date = parse_date(spp_start_date)
    spp_end_date = parse_date(spp_end_date)
    previous_month_end = parse_date(previous_month_end)

    if any(d is None for d in [start_date, end_date, spp_start_date, spp_end_date, previous_month_end]):
        return 0

    if start_date.month == spp_start_date.month:
        result = 0
    elif start_date.month == spp_end_date.month:
        result = (previous_month_end - spp_start_date + timedelta(days=1)).days // 7
    elif start_date >= spp_start_date and end_date <= spp_end_date:
        result = (previous_month_end - spp_start_date + timedelta(days=1)).days // 7
    else:
        result = 0
    return result


 
# def UK_PS_SPP_WEEKS_TLL_NOW_NEW(start_date, end_date, spp_start_date, spp_end_date, previous_month_end):
#     if start_date.month == spp_start_date.month:
#         result = 0
#     elif start_date.month == spp_end_date.month:
#         result = (previous_month_end - spp_start_date + timedelta(days=1)).days // 7
#     elif start_date >= spp_start_date and end_date <= spp_end_date:
#         result = (previous_month_end - spp_start_date + timedelta(days=1)).days // 7
#     else:
#         result = 0
#     return result

def parse_custom_datetime(datetime_str):
    # Parse datetime strings with format 'DD-MON-YY HH.MM.SS.FFFFFF AM/PM'
    try:
        return datetime.strptime(datetime_str, '%d-%b-%y %I.%M.%S.%f %p')
    except ValueError as e:
        print(f"Error parsing datetime: {e}")
        return None

# Adjusting UK_PS_SPP_WEEKS_TLL_NOW_NEW to use the updated parsing function
def UK_PS_SPP_WEEKS_TLL_NOW_NEW(start_date, end_date, spp_start_date_str, spp_end_date_str, previous_month_end_str):
    # Convert string dates to datetime objects if they are strings using the new parsing function
    start_date = parse_custom_datetime(start_date) if isinstance(start_date, str) else start_date
    end_date = parse_custom_datetime(end_date) if isinstance(end_date, str) else end_date
    spp_start_date = parse_custom_datetime(spp_start_date_str) if isinstance(spp_start_date_str, str) else spp_start_date_str
    spp_end_date = parse_custom_datetime(spp_end_date_str) if isinstance(spp_end_date_str, str) else spp_end_date_str
    previous_month_end = parse_custom_datetime(previous_month_end_str) if isinstance(previous_month_end_str, str) else previous_month_end_str

    if not all([start_date, end_date, spp_start_date, spp_end_date, previous_month_end]):
        # Return early if any date failed to parse
        return 0

    # Your existing logic here to calculate the number of weeks
    if start_date.month == spp_start_date.month:
        result = 0
    elif start_date.month == spp_end_date.month:
        result = (previous_month_end - spp_start_date + timedelta(days=1)).days // 7
    elif start_date >= spp_start_date and end_date <= spp_end_date:
        result = (previous_month_end - spp_start_date + timedelta(days=1)).days // 7
    else:
        result = 0
    return result







def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%d-%b-%y %I.%M.%S.%f %p') if isinstance(date_str, str) else date_str
    except ValueError as e:
        print(f"Error parsing date: {date_str} with error: {e}")
        return None

def uk_ps_networkdays(start_date, end_date):
    start_date_np = np.datetime64(start_date, 'D')
    end_date_np = np.datetime64(end_date, 'D')
    network_days = np.busday_count(start_date_np, end_date_np)
    return network_days

def uk_ps_add_working_days(start_date, num_workdays):
    start_date = parse_date(start_date)
    if start_date is None:
        return None

    result_date = start_date
    counter = 0
    while counter < num_workdays:
        result_date += timedelta(days=1)
        while result_date.weekday() >= 5:
            result_date += timedelta(days=1)
        counter += 1

    return result_date

def uk_ps_ssp_final(ssp_start_date, end_date, ssp_end_date, start_date):
    ssp_rate = config["UK_PS_SSP_FINAL"]["calculation_factors"]["ssp_rate"]
    workdays_in_week = config["UK_PS_SSP_FINAL"]["calculation_factors"]["workdays_in_week"]

    ssp_start_date = parse_date(ssp_start_date)
    end_date = parse_date(end_date)
    ssp_end_date = parse_date(ssp_end_date)
    start_date = parse_date(start_date)

    if None in [ssp_start_date, end_date, ssp_end_date, start_date]:
        return 0

    ssp_new_start_date = uk_ps_add_working_days(ssp_start_date, 3)
    if ssp_end_date < start_date or ssp_new_start_date > end_date or ssp_end_date is None or ssp_new_start_date is None:
        return 0

    if ssp_end_date.year == ssp_new_start_date.year and ssp_end_date.month == ssp_new_start_date.month:
        ssp_month = (uk_ps_networkdays(ssp_new_start_date, ssp_end_date)) / workdays_in_week * ssp_rate
    else:
        if end_date.year == ssp_new_start_date.year and end_date.month == ssp_new_start_date.month:
            ssp_month = (uk_ps_networkdays(ssp_new_start_date, end_date)) / workdays_in_week * ssp_rate
        elif ssp_end_date.year == end_date.year and ssp_end_date.month == end_date.month:
            ssp_month = uk_ps_networkdays(start_date, ssp_end_date) / workdays_in_week * ssp_rate
        else:
            ssp_month = uk_ps_networkdays(start_date, end_date) / workdays_in_week * ssp_rate

    return ssp_month


# def uk_ps_ssp_final_2024(p_SSP_start_date, p_End_date, p_SSP_end_date, p_Start_date):
#     p_SSP_new_start_date = uk_ps_add_working_days(p_SSP_start_date, 3)
#     if p_SSP_end_date < p_Start_date or p_SSP_new_start_date > p_End_date or p_SSP_end_date is None or p_SSP_new_start_date is None:
#         v_SSP_month = 0
#     elif p_SSP_new_start_date.year == p_SSP_end_date.year and p_SSP_new_start_date.month == p_SSP_end_date.month:
#         v_SSP_month = uk_ps_networkdays(p_SSP_new_start_date, p_SSP_end_date) / 5 * 116.75
#     else:
#         if p_SSP_new_start_date.year == p_End_date.year and p_SSP_new_start_date.month == p_End_date.month:
#             v_SSP_month = uk_ps_networkdays(p_SSP_new_start_date, p_End_date) / 5 * 116.75
#         elif p_SSP_end_date.year == p_End_date.year and p_SSP_end_date.month == p_End_date.month:
#             v_SSP_month = uk_ps_networkdays(p_Start_date, p_SSP_end_date) / 5 * 116.75
#         else:
#             v_SSP_month = uk_ps_networkdays(p_Start_date, p_End_date) / 5 * 116.75
#     return v_SSP_month


def uk_ps_ssp_final_2024(p_SSP_start_date, p_End_date, p_SSP_end_date, p_Start_date):
    # Load configuration values
    ssp_rate = config["UK_PS_SSP_FINAL_2024"]["calculation_factors"]["ssp_rate"]
    workdays_in_week = config["UK_PS_SSP_FINAL_2024"]["calculation_factors"]["workdays_in_week"]
    weekend_days = config["UK_PS_SSP_FINAL_2024"]["calculation_factors"]["weekend_days"]

    # Helper function to parse date strings to datetime objects
    def parse_date(date_str):
        return datetime.strptime(date_str, '%d-%b-%y %I.%M.%S.%f000000 %p') if isinstance(date_str, str) else date_str

    # Convert all date inputs to datetime objects
    p_SSP_start_date = parse_date(p_SSP_start_date)
    p_End_date = parse_date(p_End_date)
    p_SSP_end_date = parse_date(p_SSP_end_date)
    p_Start_date = parse_date(p_Start_date)

    # Additional working days are added to the start date
    p_SSP_new_start_date = p_SSP_start_date
    counter = 0
    while counter < 3:
        p_SSP_new_start_date += timedelta(days=1)
        while p_SSP_new_start_date.weekday() in weekend_days:
            p_SSP_new_start_date += timedelta(days=1)
        counter += 1

    if p_SSP_end_date is None or p_SSP_new_start_date is None:
        return 0  # Early return if any date is not defined

    # Calculate network days
    def uk_ps_networkdays(start_date, end_date):
        start_date_np = np.datetime64(start_date, 'D')
        end_date_np = np.datetime64(end_date, 'D')
        network_days = np.busday_count(start_date_np, end_date_np)
        return network_days

    # Check conditions
    if p_SSP_end_date < p_Start_date or p_SSP_new_start_date > p_End_date:
        v_SSP_month = 0
    elif p_SSP_new_start_date.year == p_SSP_end_date.year and p_SSP_new_start_date.month == p_SSP_end_date.month:
        v_SSP_month = uk_ps_networkdays(p_SSP_new_start_date, p_SSP_end_date) / workdays_in_week * ssp_rate
    else:
        if p_SSP_new_start_date.year == p_End_date.year and p_SSP_new_start_date.month == p_End_date.month:
            v_SSP_month = uk_ps_networkdays(p_SSP_new_start_date, p_End_date) / workdays_in_week * ssp_rate
        elif p_SSP_end_date.year == p_End_date.year and p_SSP_end_date.month == p_End_date.month:
            v_SSP_month = uk_ps_networkdays(p_Start_date, p_SSP_end_date) / workdays_in_week * ssp_rate
        else:
            v_SSP_month = uk_ps_networkdays(p_Start_date, p_End_date) / workdays_in_week * ssp_rate

    return v_SSP_month

def uk_ps_unpaid_streak(p_LEAVE_START_DATE_TIME, p_payroll_process_start_date, p_payroll_process_end_date, p_LEAVE_END_DATE_TIME):
    # Helper function to parse date strings to datetime objects
    def parse_date(date_str):
        return datetime.strptime(date_str, '%d-%b-%y %I.%M.%S.%f000000 %p') if isinstance(date_str, str) else date_str

    # Convert dates to datetime objects if they are not already
    p_LEAVE_START_DATE_TIME = parse_date(p_LEAVE_START_DATE_TIME)
    p_payroll_process_start_date = parse_date(p_payroll_process_start_date)
    p_payroll_process_end_date = parse_date(p_payroll_process_end_date)
    p_LEAVE_END_DATE_TIME = parse_date(p_LEAVE_END_DATE_TIME)

    v_sap = 0
    if p_LEAVE_START_DATE_TIME >= p_payroll_process_start_date and p_LEAVE_END_DATE_TIME <= p_payroll_process_end_date:
        v_sap = (p_LEAVE_END_DATE_TIME - p_LEAVE_START_DATE_TIME).days + 1
    elif p_LEAVE_START_DATE_TIME >= p_payroll_process_start_date and p_LEAVE_START_DATE_TIME <= p_payroll_process_end_date:
        v_sap = (p_payroll_process_end_date - p_LEAVE_START_DATE_TIME).days + 1
    elif p_LEAVE_END_DATE_TIME >= p_payroll_process_start_date and p_LEAVE_END_DATE_TIME <= p_payroll_process_end_date:
        v_sap = (p_LEAVE_END_DATE_TIME - p_payroll_process_start_date).days + 1
    return v_sap

def uk_ps_ytd_absence_entitlement_2(v_emp_num, p_ytd_start_date, p_ytd_end_date, v_payroll_process_date, v_client_id):
    days_in_year = config["general"]["days_in_year"]

    # Helper function to parse date strings to datetime objects
    def parse_date(date_str):
        return datetime.strptime(date_str, '%Y-%m-%d') if isinstance(date_str, str) else date_str

    v_total_ytd_absence_entitlement = 0
    v_ytd_start_date = parse_date(p_ytd_start_date)
    v_ytd_end_date = parse_date(p_ytd_end_date)
    v_current_date = v_ytd_start_date.replace(day=1)

    while v_current_date <= v_ytd_end_date.replace(day=1):
        v_start_date = v_current_date.replace(day=1)
        v_end_date = (v_current_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        v_sal_last_update_date = fetch_latest_salary_update(v_emp_num, v_end_date, v_payroll_process_date, v_client_id)
        v_annual_salary = fetch_annual_salary(v_emp_num, v_sal_last_update_date, v_client_id)

        if v_ytd_end_date.month == v_end_date.month:
            v_absence_entitlement_days = uk_ps_absence_entitlement_days_1(v_emp_num, v_start_date, v_end_date, v_payroll_process_date, v_client_id)
        else:
            v_absence_entitlement_days = uk_ps_absence_entitlement_days(v_emp_num, v_start_date, v_end_date, v_payroll_process_date, v_client_id)

        v_monthly_absence_entitlement = (v_absence_entitlement_days * v_annual_salary / days_in_year)
        v_total_ytd_absence_entitlement += v_monthly_absence_entitlement

        v_current_date = v_current_date.replace(day=1) + timedelta(days=32)
    
    return v_total_ytd_absence_entitlement




def uk_ps_ytd_maternity(v_emp_num, v_start_date, v_end_date, v_maternity_gross, v_client_id):
    v_smp_final_value = 0
    v_previous_month_end = v_start_date - timedelta(days=1)
    
    # Simulated query to fetch data from the database
    # You need to replace this with your actual database query
    # This is just a placeholder and may not work as is
    maternity_leave_data = [
        {'EMPLOYEE_ID': v_emp_num, 'LEAVE_START_DATE_TIME': datetime(2024, 1, 1), 'LEAVE_END_DATE_TIME': datetime(2024, 1, 31)},
        {'EMPLOYEE_ID': v_emp_num, 'LEAVE_START_DATE_TIME': datetime(2024, 2, 1), 'LEAVE_END_DATE_TIME': datetime(2024, 2, 29)}
        # Add more data as needed
    ]

    for j in maternity_leave_data:
        v_smp_start_date = j['LEAVE_START_DATE_TIME']
        v_smp_end_date = j['LEAVE_END_DATE_TIME'] or v_end_date

        # Placeholder function calls
        v_uk_smp_weeks_tll_now = UK_PS_SAP_SMP_WEEKS_TLL_NOW(v_start_date, v_end_date, v_smp_start_date, v_smp_end_date, v_previous_month_end)
        v_uk_smp_month_days = UK_PS_SAP_SMP_MONTH_DAYS_NEW(v_start_date, v_end_date, v_smp_start_date, v_previous_month_end, v_smp_end_date)
        v_uk_smp_month_weeks = UK_PS_SAP_SMP_MONTH_WEEKS_NEW(v_start_date, v_end_date, v_smp_start_date, v_smp_end_date, v_uk_smp_month_days)

        # Placeholder function call
        v_smp_final_value += UK_PS_SAP_SMP_FINAL_NEW(v_maternity_gross, v_uk_smp_weeks_tll_now, v_uk_smp_month_weeks)

    return v_smp_final_value


def uk_ps_ytd_paternity(v_emp_num, v_start_date, v_end_date, v_paternity_gross, v_client_id):
    V_SPP_FINAL_VALUE = 0
    v_previous_month_end = v_start_date - timedelta(days=1)

    # Simulated paternity leave data
    paternity_leave_data = [
    {'EMPLOYEE_ID': v_emp_num, 'LEAVE_START_DATE_TIME': datetime(2024, 1, 1), 'LEAVE_END_DATE_TIME': datetime(2024, 1, 31), 'LEAVE_TYPE': 'GB Paternity Leave', 'CLIENT_ID': '123'},
    {'EMPLOYEE_ID': v_emp_num, 'LEAVE_START_DATE_TIME': datetime(2024, 2, 1), 'LEAVE_END_DATE_TIME': datetime(2024, 2, 29), 'LEAVE_TYPE': 'GB Paternity Leave', 'CLIENT_ID': '456'}
    # Add more data as needed
]


    for leave_instance in paternity_leave_data:
        if leave_instance['EMPLOYEE_ID'] == v_emp_num and leave_instance['LEAVE_TYPE'] == 'GB Paternity Leave' and leave_instance['CLIENT_ID'] == v_client_id:
            v_spp_start_date = leave_instance['LEAVE_START_DATE_TIME'].strftime('%m/%d/%Y')
            v_spp_end_date = leave_instance['LEAVE_END_DATE_TIME'].strftime('%m/%d/%Y')

            # Replace the following function calls with the appropriate functions for paternity leave calculations
            V_UK_SPP_WEEKS_TLL_NOW = UK_PS_SPP_WEEKS_TLL_NOW_NEW(v_start_date, v_end_date, v_spp_start_date, v_spp_end_date, v_previous_month_end)
            V_UK_PS_SPP_MONTH_DAYS = UK_PS_SPP_MONTH_DAYS_NEW(v_start_date, v_end_date, v_spp_start_date, v_previous_month_end, v_spp_end_date)
            V_UK_SPP_MONTH_WEEKS = UK_PS_SPP_MONTH_WEEKS_NEW(v_start_date, v_end_date, v_spp_start_date, v_spp_end_date, V_UK_PS_SPP_MONTH_DAYS)

            V_SPP_FINAL_VALUE += UK_PS_SPP_FINAL_NEW_2024(v_paternity_gross, V_UK_SPP_MONTH_WEEKS)

    return V_SPP_FINAL_VALUE


def uk_ps_ytd_salary_2(v_emp_num, p_ytd_start_date, p_ytd_end_date, v_client_id):
    v_total_ytd_salary = 0
    v_ytd_start_date = datetime.strptime(p_ytd_start_date, '%Y-%m-%d')
    v_ytd_end_date = datetime.strptime(p_ytd_end_date, '%Y-%m-%d')
    v_current_date = v_ytd_start_date.replace(day=1)

    while v_current_date <= v_ytd_end_date.replace(day=1):
        v_start_date = v_current_date.replace(day=1)
        v_end_date = (v_current_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        v_annual_salary, v_effective_start_date, v_effective_end_date = fetch_annual_salary_1(v_emp_num, v_start_date, v_end_date, v_client_id)

        if v_effective_start_date is not None and v_effective_end_date is not None:
            v_monthly_salary = v_annual_salary / 12
            v_total_ytd_salary += v_monthly_salary

        v_current_date = v_current_date.replace(day=1) + timedelta(days=32)

    return v_total_ytd_salary


def calculate_prorated_salary(v_annual_salary, HIRE_DATE, end_date):
    total_days_in_month = (end_date - HIRE_DATE.replace(day=1)).days + 1
    worked_days_in_month = (end_date - HIRE_DATE).days + 1
    monthly_salary = v_annual_salary / 12
    prorated_salary = (monthly_salary / total_days_in_month) * worked_days_in_month
    return prorated_salary
