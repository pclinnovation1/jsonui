from pymongo import MongoClient
from datetime import datetime, timedelta
import re
import math
import numpy as np
from dateutil import parser
import sys
import config

from final_functions_01 import get_previous_month_end, uk_ps_ytd_absence_entitlement_2, uk_ps_absence_entitlement_days_1, uk_ps_add_working_days, calculate_cost_to_employer, calculate_net_income, calculate_nic_tax_employee_2024, calculate_nic_tax_employer_2024, calculate_pension_contribution_employee, calculate_pension_contribution_employer, calculate_student_loan_repayment, calculate_take_home, calculate_tax_normal_with_codes5, calculate_tax_normal_with_codes8, uk_ps_networkdays, uk_ps_rp_sal_deduction, UK_PS_SALARY_RETROACTIVE, UK_PS_SAP_SMP_FINAL_NEW_2024, UK_PS_SAP_SMP_MONTH_DAYS_NEW, UK_PS_SAP_SMP_MONTH_WEEKS_NEW, UK_PS_SAP_SMP_WEEKS_TLL_NOW, UK_PS_SPP_FINAL_NEW_2024, UK_PS_SPP_MONTH_DAYS, parse_date, UK_PS_SPP_MONTH_DAYS_NEW, UK_PS_SPP_MONTH_WEEKS_NEW, UK_PS_SPP_WEEKS_TLL_NOW_NEW, UK_PS_SPP_WEEKS_TLL_NOW_NEW, uk_ps_networkdays, uk_ps_add_working_days, uk_ps_networkdays, uk_ps_add_working_days, uk_ps_ssp_final_2024, uk_ps_unpaid_streak, uk_ps_ytd_maternity, uk_ps_ytd_paternity, fetch_annual_salary_1, uk_ps_ytd_salary_2, uk_ps_ytd_salary_deduction

from final_functions_02 import fetch_spp_ytd, fetch_smp_ytd, fetch_salary_ytd, uk_ps_absence_entitlement_days_1, fetch_dates_from_db, fetch_last_payroll_period, fetch_salary_creation_date, fetch_annual_salary, fetch_maternity_leave_dates, fetch_previous_maternity_ytd, fetch_paternity_leave_dates, fetch_sickness_leave_dates, fetch_absence_entitlement_retro, fetch_absence_entitlement_retro_ytd, fetch_salary_ytd_previous_period, fetch_pension_contribution, fetch_pension_details, fetch_pension_ytd, fetch_pre_statutory_deduction, fetch_niable_gross_till_date, fetch_ni_category, fetch_ytd_value, insert_ni_employee_contribution, insert_ni_employer_contribution, fetch_tax_deduction_with_pension, fetch_taxable_gross_till_date, fetch_paye_till_date, fetch_tax_code_and_basis, update_ytd_for_april, insert_sickness_data, insert_maternity_data, insert_paternity_data, insert_pension_employee_data, insert_pension_employer_data, insert_paye_data, insert_tax_gross

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

def uk_ps_proc_2_bal_calc(v_payroll_period, v_client_id):
    # Initialize MongoDB client and database
    client = get_mongo_connection()
    db = client[config.DATABASE_NAME]

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


    # Initialize all variables...
    # (Variable initialization remains unchanged)

    v_start_date = None
    v_end_date = None
    v_payroll_process_end_date = None
    v_previous_month_end = None
    v_sal_last_update_date = None
    v_payroll_process_date = None

    v_smp_start_date = None
    v_smp_end_date = None
    v_spp_start_date = None
    v_spp_end_date = None
    v_ssp_start_date = None
    v_ssp_end_date = None

    # Varchar
    v_emp_num = ''
    v_last_payroll_period = ''
    v_ni_category = ''
    v_tax_code = ''
    v_tax_basis = ''
    v_student_loan_plan = ''

    # Number
    v_salary = 0
    v_annual_salary = 0
    v_deduction = 0
    v_salary_ytd = 0
    v_previous_salary_ytd = 0
    v_previous_salary_retro_ytd = 0
    v_salary_as_effective_dates = 0
    v_month_number = 0

    v_uk_smp_weeks_till_now = 0
    v_uk_smp_month_days = 0
    v_uk_smp_month_weeks = 0
    v_smp_final_value = 0
    v_smp_ytd = 0
    v_maternity_gross = 0
    v_maternity_ytd_days = 0
    v_ytd_days = 0
    v_previous_maternity_ytd = 0
    v_previous_maternity_retro_ytd = 0

    v_uk_spp_weeks_till_now = 0
    v_uk_spp_month_days = 0
    v_uk_spp_month_weeks = 0
    v_spp_final_value = 0
    v_spp_ytd = 0
    v_previous_paternity_ytd = 0
    v_previous_paternity_retro_ytd = 0
    v_paternity_gross = 0
    v_paternity_ytd_days = 0

    v_ssp_final_value = 0
    v_ssp_ytd = 0
    v_previous_sickness_ytd = 0
    v_previous_sickness_retro_ytd = 0

    v_regular_earnings_gross_addition = 0
    v_absences_gross_addition = 0
    v_irregular_earnings_gross_addition = 0
    v_gross_pay = 0

    v_regular_earnings_pension_contribution = 0
    v_absences_pension_contribution = 0
    v_absences_pension_deduction = 0
    v_pension_contribution = 0
    v_employer_pension_contribution = 0
    v_employee_pension_contribution = 0
    v_pension_employer_ytd_occupational = 0
    v_pension_employee_ytd_occupational = 0
    v_pension_employer_ytd = 0
    v_pension_employee_ytd = 0
    v_pension_employee = 0
    v_pension_employer = 0

    v_ni_pre_statutory_deduction = 0
    v_ni_gross_pay = 0
    v_ni_employee_ytd = 0
    v_nic_employee = 0
    v_ni_employer_ytd = 0
    v_nic_employer = 0
    v_niable_gross_till_date = 0

    v_tax_deduction_with_pension = 0
    v_tax_deduction_without_pension = 0
    v_tax_gross = 0
    v_taxable_gross_till_date = 0
    v_paye_till_date = 0

    v_student_loan_ytd = 0
    v_student_loan = 0

    v_employer_taxes = 0
    v_taxable_benefits_in_kind = 0
    v_tax_deductions = 0
    v_voluntary_deductions = 0
    v_national_insurance_deductions = 0
    v_employer_charges = 0
    v_absences = 0
    v_involuntary_deductions = 0
    v_direct_payments = 0
    v_pre_statutory_deductions_with_pension = 0
    v_pre_statutory_deductions_without_pension = 0

    v_absence_salary_deduction_hourly = 0
    v_absence_salary_deduction_hourly_ytd = 0
    v_absence_entitlement_days = 0
    v_absence_entitlement = 0
    v_absence_entitlement_ytd = 0
    v_absence_entitlement_retro_ytd = 0
    v_salary_retroactive = 0
    v_normal_work_hours = 0
    v_absence_entitlement_hours = 0
    v_absence_entitlement_retro = 0
    v_absence_entitlement_hourly_retro = 0

    # Handling Dates
    try:
        v_start_date, v_end_date, v_payroll_process_date, v_payroll_process_end_date, v_month_number = fetch_dates_from_db(v_payroll_period, v_client_id)
        print()
        print(f"Dates: Start Date - {v_start_date}, End Date - {v_end_date}, Payroll Process Date - {v_payroll_process_date}, Payroll Process End Date - {v_payroll_process_end_date}, Month Number - {v_month_number}")
        print(f"Dates: Start Date - {type(v_start_date)}, End Date - {v_end_date}, Payroll Process Date - {v_payroll_process_date}, Payroll Process End Date - {v_payroll_process_end_date}, Month Number - {v_month_number}")
    except Exception as e:
        print(f"Error fetching dates: {e}")
        return

    # No need to convert v_start_date again as it's already a datetime object
    print()
    v_previous_month_end = get_previous_month_end(v_start_date)
    print(f"Previous Month End: {v_previous_month_end}")
    print()
    try:
        v_last_payroll_period = fetch_last_payroll_period(v_start_date, v_client_id)  # Pass the datetime object here
        print(v_last_payroll_period)
        if v_last_payroll_period is None:
            v_last_payroll_period = f"12 {v_start_date.year - 1} Calendar Month"
        print(f"Last Payroll Period: {v_last_payroll_period}")
    except Exception as e:
        print(f"Error fetching last payroll period: {e}")
        return
    print()

    # Fetching employees from MongoDB collection
    employees = list(employee_information_collection.find({"CLIENT_ID": v_client_id, "EMPLOYEE_NUMBER": 104}, {"EMPLOYEE_NUMBER": 1}))
    print("employee list: ", employees)
    print("total number of employees: ", len(employees))
    print()
    # running calculation for each employee
    for employee in employees:
        v_emp_num = employee['EMPLOYEE_NUMBER']
        print("v_empployee_number: ", v_emp_num, "  ", type(v_emp_num))
        print()
        v_sal_last_update_date = fetch_salary_creation_date(v_emp_num, v_end_date, v_payroll_process_date, v_client_id)

        print("v_sal_last_update_date: ", v_sal_last_update_date, "  ", type(v_sal_last_update_date))
        print()
        print("v_client_id: ",v_client_id, "  ", type(v_client_id))
        print()
        if v_sal_last_update_date:
            v_annual_salary = fetch_annual_salary(v_emp_num, v_sal_last_update_date, v_client_id)
            v_salary = v_annual_salary / 12
            print(f"Employee: {v_emp_num}, Annual Salary: {v_annual_salary}, Monthly Salary: {v_salary}")
        else:
            print(f"No salary data found for employee: {v_emp_num}")

        # -----------------------------------------------------------------------------------------------
        # -- Statutory MATERNITY Pay --------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------------
        # Handle Statutory Maternity Pay
        v_smp_final_value = 0
        v_maternity_ytd_days = 0

        maternity_leaves = fetch_maternity_leave_dates(v_emp_num, v_client_id)
        for leave in maternity_leaves:
            v_smp_start_date, v_smp_end_date = leave
            v_smp_end_date = v_smp_end_date if v_smp_end_date else v_end_date
            
            print(f"Maternity Leave Period: Start Date - {v_smp_start_date}, End Date - {v_smp_end_date}")

            # Assuming the existence of Python equivalents for your PL/SQL functions
            v_uk_smp_weeks_till_now = UK_PS_SAP_SMP_WEEKS_TLL_NOW(v_start_date, v_end_date, v_smp_start_date, v_smp_end_date, v_previous_month_end)
            v_uk_smp_month_days = UK_PS_SAP_SMP_MONTH_DAYS_NEW(v_start_date, v_end_date, v_smp_start_date, v_previous_month_end, v_smp_end_date)
            v_uk_smp_month_weeks = UK_PS_SAP_SMP_MONTH_WEEKS_NEW(v_start_date, v_end_date, v_smp_start_date, v_smp_end_date, v_uk_smp_month_days)

            v_smp_final_value += UK_PS_SAP_SMP_FINAL_NEW_2024(v_salary, v_uk_smp_weeks_till_now, v_uk_smp_month_weeks)
            v_maternity_ytd_days += v_uk_smp_month_days  # Assuming this is calculated from 01/04/2023 to v_end_date

        # Calculate YTD maternity gross
        v_maternity_gross = uk_ps_ytd_salary_deduction(v_emp_num, '2024-04-01 00:00:00', v_end_date, 'GB Maternity Leave', v_client_id)
        # v_ytd_days = (v_end_date - datetime.strptime('2024-04-01 00:00:00', '%Y-%m-%d')).days
        v_ytd_days = (datetime.strptime(v_end_date, '%Y-%m-%d %H:%M:%S') - datetime.strptime('2024-04-01 00:00:00', '%Y-%m-%d %H:%M:%S')).days


        if v_maternity_ytd_days > 0:
            v_maternity_gross *= v_ytd_days / v_maternity_ytd_days
            
            print(f"Adjusted Maternity Gross Deduction: {v_maternity_gross}")

        # v_smp_ytd = uk_ps_ytd_maternity(v_emp_num, v_start_date, v_end_date, v_maternity_gross, v_client_id) + fetch_previous_maternity_ytd(v_emp_num, v_last_payroll_period, v_client_id)
        v_smp_ytd = fetch_smp_ytd(v_emp_num, 'Absences', 'Statutory Maternity', v_last_payroll_period, v_client_id)

        v_smp_ytd += v_smp_final_value

        print(f"YTD SMP for Employee: {v_smp_ytd}")
        
        if v_smp_final_value > 0:
            # Inserting maternity data into MongoDB collection
            db.maternity_data.insert_one({
                "EMPLOYEE_NUMBER": v_emp_num,
                "PAYROLL_PERIOD": v_payroll_period,
                "SMP_FINAL_VALUE": v_smp_final_value,
                "SMP_YTD": v_smp_ytd,
                "CLIENT_ID": v_client_id
            })
            
            print(f"Inserting Maternity Data: SMP Final Value - {v_smp_final_value}, SMP YTD - {v_smp_ytd}")

        # Handle Statutory Paternity Pay
        v_spp_final_value = 0

        paternity_leaves = fetch_paternity_leave_dates(v_emp_num, v_client_id)
        for leave in paternity_leaves:
            v_spp_start_date, v_spp_end_date = leave
            v_spp_end_date = v_spp_end_date if v_spp_end_date else v_end_date

            # Calculations using Python equivalents of your functions
            v_uk_spp_weeks_till_now = UK_PS_SPP_WEEKS_TLL_NOW_NEW(v_start_date, v_end_date, v_spp_start_date, v_spp_end_date, v_previous_month_end)
            v_uk_spp_month_days = UK_PS_SPP_MONTH_DAYS_NEW(v_start_date, v_end_date, v_spp_start_date, v_previous_month_end, v_spp_end_date)
            v_uk_spp_month_weeks = UK_PS_SPP_MONTH_WEEKS_NEW(v_start_date, v_end_date, v_spp_start_date, v_spp_end_date, v_uk_spp_month_days)

            v_spp_final_value += UK_PS_SPP_FINAL_NEW_2024(v_salary, v_uk_spp_month_weeks)
            
            # Debugging outputs
            print("v_spp_start_date:", v_spp_start_date)
            print("v_spp_end_date:", v_spp_end_date)
            print("v_uk_spp_weeks_till_now:", v_uk_spp_weeks_till_now)
            print("v_uk_spp_month_days:", v_uk_spp_month_days)
            print("v_uk_spp_month_weeks:", v_uk_spp_month_weeks)
            print("v_spp_final_value:", v_spp_final_value)

        v_paternity_gross = uk_ps_ytd_salary_deduction(v_emp_num, '2024-04-01 00:00:00', v_end_date, 'GB Paternity Leave', v_client_id)
        # v_ytd_days = (v_end_date - datetime.strptime('2024-04-01 00:00:00', '%Y-%m-%d')).days
        v_ytd_days = (datetime.strptime(v_end_date, '%Y-%m-%d %H:%M:%S') - datetime.strptime('2024-04-01 00:00:00', '%Y-%m-%d %H:%M:%S')).days

        print("v_paternity_gross:", v_paternity_gross)
        print("v_ytd_days:", v_ytd_days)
        print()
        print()

        if v_paternity_ytd_days > 0:
            v_paternity_gross *= v_ytd_days / v_paternity_ytd_days

        v_spp_ytd = fetch_spp_ytd(v_emp_num, 'Absences', 'Statutory Paternity', v_last_payroll_period, v_client_id)
        print()
        v_spp_ytd += v_spp_final_value

        if v_spp_final_value > 0:
            db.paternity_data.insert_one({
                "EMPLOYEE_NUMBER": v_emp_num,
                "PAYROLL_PERIOD": v_payroll_period,
                "SPP_FINAL_VALUE": v_spp_final_value,
                "SPP_YTD": v_spp_ytd,
                "CLIENT_ID": v_client_id
            })

        # Handle Statutory Sickness Pay
        v_ssp_final_value = 0
        v_ssp_ytd = 0

        sickness_leaves = fetch_sickness_leave_dates(v_emp_num, v_client_id)
        for leave in sickness_leaves:
            v_ssp_start_date, v_ssp_end_date = leave
            v_ssp_end_date = v_ssp_end_date if v_ssp_end_date else v_end_date

            v_ssp_final_value += uk_ps_ssp_final_2024(v_ssp_start_date, v_end_date, v_ssp_end_date, v_start_date)
            v_ssp_ytd += uk_ps_ssp_final_2024(v_ssp_start_date, v_end_date, v_ssp_end_date, datetime.strptime('2024-04-01 00:00:00', '%Y-%m-%d'))
            
            print("v_ssp_start_date:", v_ssp_start_date)
            print("v_ssp_end_date:", v_ssp_end_date)
            print("v_ssp_final_value:", v_ssp_final_value)
            print("v_ssp_ytd:", v_ssp_ytd)

        if v_ssp_final_value > 0:
            db.sickness_data.insert_one({
                "EMPLOYEE_NUMBER": v_emp_num,
                "PAYROLL_PERIOD": v_payroll_period,
                "SSP_FINAL_VALUE": v_ssp_final_value,
                "SSP_YTD": v_ssp_ytd,
                "CLIENT_ID": v_client_id
            })

        # Salary Pay Calculations
        fiscal_year_start = '2024-04-01'
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        print("fiscal_year_start:", fiscal_year_start)
        print("current_date:", current_date)
        
        v_absence_entitlement_ytd = uk_ps_ytd_absence_entitlement_2(v_emp_num, fiscal_year_start, current_date, current_date, v_client_id)
        v_absence_entitlement_days = uk_ps_absence_entitlement_days_1(v_emp_num, v_start_date, v_end_date, current_date, v_client_id)

        print("v_absence_entitlement_ytd:", v_absence_entitlement_ytd)
        print("v_absence_entitlement_days:", v_absence_entitlement_days)

        v_absence_entitlement = (v_absence_entitlement_days * v_salary / 260)
        v_salary -= v_absence_entitlement

        print("v_absence_entitlement:", v_absence_entitlement)
        print("v_salary after deduction:", v_salary)

        v_salary_ytd = fetch_salary_ytd(v_emp_num, 'Regular Earnings', 'Salary', v_last_payroll_period, v_client_id)

        if v_payroll_period.startswith('1 20'):
            v_salary_ytd = 0

        v_salary_ytd += v_salary
        print("v_salary_ytd after adjustment:", v_salary_ytd)

        balance_calculation_report_collection.insert_one({
            "EMPLOYEE_NUMBER": v_emp_num,
            "PAYROLL_PERIOD": v_payroll_period,
            "BALANCE_CATEGORY": 'Regular Earnings',
            "ELEMENT_NAME": 'Salary',
            "CLIENT_ID": v_client_id,
            "CURRENT_VALUE": v_salary,
            "YEAR_TO_DATE": v_salary_ytd
        })

        # Gross Pay Calculations
        v_gross_pay = v_salary
        print("v_gross_pay:", v_gross_pay)

        # Pension Pay Calculations
        v_pension_contribution = v_salary
        v_employer_pension_contribution, v_employee_pension_contribution = fetch_pension_details(v_emp_num, v_client_id)

        print("v_pension_contribution:", v_pension_contribution)
        print("v_employer_pension_contribution:", v_employer_pension_contribution)
        print("v_employee_pension_contribution:", v_employee_pension_contribution)

        if v_pension_contribution >= v_gross_pay:
            v_pension_contribution = v_gross_pay

        print("Adjusted v_pension_contribution:", v_pension_contribution)

        # v_pension_employer = calculate_pension_contribution_employer(v_pension_contribution, v_employer_pension_contribution / 100)
        # v_pension_employee = calculate_pension_contribution_employee(v_pension_contribution, v_employee_pension_contribution / 100)
        v_pension_employer = calculate_pension_contribution_employer(v_pension_contribution)
        v_pension_employee = calculate_pension_contribution_employee(v_pension_contribution)

        print("v_pension_employer:", v_pension_employer)
        print("v_pension_employee:", v_pension_employee)

        v_pension_employer_ytd = fetch_pension_ytd(v_emp_num, 'Employer Charges', 'LG Pension Employers Contribution', v_last_payroll_period, v_client_id)
        v_pension_employee_ytd = fetch_pension_ytd(v_emp_num, 'Pre-Statutory Deductions With Pension', 'LG Pension Employees Contribution', v_last_payroll_period, v_client_id)

        v_pension_employer_ytd += v_pension_employer
        v_pension_employee_ytd += v_pension_employee

        print("v_pension_employer_ytd:", v_pension_employer_ytd)
        print("v_pension_employee_ytd:", v_pension_employee_ytd)

        db.pension_employee_data.insert_one({
            "EMPLOYEE_NUMBER": v_emp_num,
            "PAYROLL_PERIOD": v_payroll_period,
            "PENSION_EMPLOYEE": v_pension_employee,
            "PENSION_EMPLOYEE_YTD": v_pension_employee_ytd,
            "CLIENT_ID": v_client_id
        })

        db.pension_employer_data.insert_one({
            "EMPLOYEE_NUMBER": v_emp_num,
            "PAYROLL_PERIOD": v_payroll_period,
            "PENSION_EMPLOYER": v_pension_employer,
            "PENSION_EMPLOYER_YTD": v_pension_employer_ytd,
            "CLIENT_ID": v_client_id
        })

        # National Insurance Calculations
        v_ni_pre_statutory_deduction = fetch_pre_statutory_deduction(v_emp_num, v_payroll_period, v_client_id)
        v_niable_gross_till_date = fetch_niable_gross_till_date(v_emp_num, v_last_payroll_period, v_client_id)
        v_ni_category = fetch_ni_category(v_emp_num, v_client_id)

        print("v_ni_pre_statutory_deduction:", v_ni_pre_statutory_deduction)
        print("v_niable_gross_till_date:", v_niable_gross_till_date)
        print("v_ni_category:", v_ni_category)

        if v_gross_pay is not None and v_ni_pre_statutory_deduction is not None:
            v_ni_gross_pay = v_gross_pay - v_ni_pre_statutory_deduction
        else:
            v_ni_gross_pay = v_gross_pay or 0

        print("v_ni_gross_pay:", v_ni_gross_pay)

        v_ni_employee_ytd = fetch_ytd_value(v_emp_num, 'National Insurance Deductions', 'NI Employee', v_last_payroll_period, v_client_id)
        v_ni_employer_ytd = fetch_ytd_value(v_emp_num, 'Employer Taxes', 'NI Employer', v_last_payroll_period, v_client_id)

        print("v_ni_employee_ytd:", v_ni_employee_ytd)
        print("v_ni_employer_ytd:", v_ni_employer_ytd)

        v_nic_employee = calculate_nic_tax_employee_2024(v_ni_gross_pay, v_ni_category)
        v_nic_employer = calculate_nic_tax_employer_2024(v_ni_gross_pay, v_ni_category)

        v_ni_employee_ytd += v_nic_employee
        v_ni_employer_ytd += v_nic_employer

        print("Updated v_ni_employee_ytd:", v_ni_employee_ytd)
        print("Updated v_ni_employer_ytd:", v_ni_employer_ytd)

        db.ni_employee_contribution.insert_one({
            "EMPLOYEE_NUMBER": v_emp_num,
            "PAYROLL_PERIOD": v_payroll_period,
            "NI_EMPLOYEE": v_nic_employee,
            "NI_EMPLOYEE_YTD": v_ni_employee_ytd,
            "CLIENT_ID": v_client_id
        })

        db.ni_employer_contribution.insert_one({
            "EMPLOYEE_NUMBER": v_emp_num,
            "PAYROLL_PERIOD": v_payroll_period,
            "NI_EMPLOYER": v_nic_employer,
            "NI_EMPLOYER_YTD": v_ni_employer_ytd,
            "CLIENT_ID": v_client_id
        })

        # PAYE Calculations
        v_tax_deduction_with_pension = fetch_tax_deduction_with_pension(v_emp_num, v_payroll_period, v_client_id)
        v_taxable_gross_till_date = fetch_taxable_gross_till_date(v_emp_num, v_last_payroll_period, v_client_id)
        v_paye_till_date = fetch_paye_till_date(v_emp_num, v_last_payroll_period, v_client_id)

        print("v_tax_deduction_with_pension:", v_tax_deduction_with_pension)
        print("v_taxable_gross_till_date:", v_taxable_gross_till_date)
        print("v_paye_till_date:", v_paye_till_date)

        v_tax_code, v_tax_basis = fetch_tax_code_and_basis(v_emp_num, v_client_id)

        print("v_tax_code:", v_tax_code)
        print("v_tax_basis:", v_tax_basis)

        if all(v is not None for v in [v_gross_pay, v_tax_deduction_with_pension, v_pension_employee]):
            v_tax_gross = v_gross_pay - v_tax_deduction_with_pension
        else:
            v_tax_gross = 0

        print("v_tax_gross:", v_tax_gross)

        db.tax_gross.insert_one({
            "EMPLOYEE_NUMBER": v_emp_num,
            "PAYROLL_PERIOD": v_payroll_period,
            "TAX_GROSS": v_tax_gross,
            "TAXABLE_GROSS_TILL_DATE": v_taxable_gross_till_date + v_tax_gross,
            "CLIENT_ID": v_client_id
        })

        if v_tax_basis == 'C':
            v_paye = calculate_tax_normal_with_codes8(v_tax_code, v_tax_gross, v_taxable_gross_till_date, v_paye_till_date, v_month_number)
        else:
            v_paye = calculate_tax_normal_with_codes5(v_tax_code, v_tax_gross, v_pension_employee)

        print("Calculated PAYE:", v_paye)

        v_paye_ytd = v_paye_till_date + v_paye

        db.paye_data.insert_one({
            "EMPLOYEE_NUMBER": v_emp_num,
            "PAYROLL_PERIOD": v_payroll_period,
            "PAYE": v_paye,
            "PAYE_YTD": v_paye_ytd,
            "CLIENT_ID": v_client_id
        })

        # Update GROSS_PAY
        db.balance_calculation_report.update_one(
            {"EMPLOYEE_NUMBER": v_emp_num, "PAYROLL_PERIOD": v_payroll_period, "CLIENT_ID": v_client_id},
            {"$set": {"GROSS_PAY": v_gross_pay}}
        )

        if v_payroll_period.startswith('1'):
            db.balance_calculation_report.update_many(
                {"CLIENT_ID": v_client_id},
                {"$set": {"YEAR_TO_DATE": "$CURRENT_VALUE"}}
            )

        print("Updated GROSS_PAY and YEAR_TO_DATE for client", v_client_id)

# Example call to the function
uk_ps_proc_2_bal_calc('1 2024 Calendar Month', 'Bansal Groups_22_03_2024')