import ast
import requests, json
import concurrent.futures
from datetime import datetime
from flask import Flask, jsonify
from pymongo import MongoClient
import os
from pprint import pprint
import re
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate  # Correct import for PromptTemplate
from langchain.chains import LLMChain  # Correct import for LLMChain
# Suppress Deprecation Warnings
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Flask App initialization
app = Flask(__name__)

MONGODB_URI = "mongodb://oras_user:oras_pass@172.191.245.199:27017/oras"
# localhost:27017/testing"
DATABASE_NAME = "oras"

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]


# Prompts Definition
base_prompt = """
You are an intelligent assistant responsible for analyzing user prompts and generating relevant field names for various HR reports. Your job is to understand the user's prompt and provide only the relevant field names from the schemas listed below.
 
Here are the available schemas and fields you can work with:
 
HRM_employee_details schema:
    person_number: Unique ID assigned to the employee.
    person_name: Full name of the employee.
    organization_unit: The unit or department the employee belongs to.
    position: Job position or title of the employee.
    manager_name: Name of the employee's direct manager.
    employment_status: Current employment status (e.g., Active, Terminated).
    effective_start_date: Date the employee started in the current role.
    effective_end_date: Date the employee’s role or employment ended.
    business_unit: Business unit the employee belongs to.
    department: Department the employee is part of.
    working_hours: Number of hours worked per week.
    full_time_or_part_time: Indicates if the employee is full-time or part-time.
    fte: Full-time equivalent value.
    retirement_date: The employee's anticipated or actual retirement date.
    location: Physical location of the employee.
    working_as_manager: Indicates if the employee works as a manager.
    working_from_home: Indicates if the employee works remotely.
    hire_date: The employee's hire date.
    termination_date: The employee's termination date.
    worker_category: Blue collar or white collar etc.(BC or WC)
 
HRM_personal_details schema:
    person_number: Unique ID assigned to the employee.
    person_name: Full name of the employee.
    date_of_birth: Birthdate of the employee.
    home_country: Country where the employee resides.
    citizenship_status: Citizenship status of the employee.
    nationality: Nationality of the employee.
    gender: Gender of the employee.
 
HRM_salary_details schema:
    person_number: Unique ID assigned to the employee.
    person_name: Full name of the employee.
    base_salary: The employee's base salary.
    salary_effective_date: The date the current salary took effect.
    currency: The currency in which the salary is paid.
    fte: Full-time equivalent value.

PGM_goals schema:
    goal_id: Unique identifier for the goal.
    goal_name: Name or title of the goal.
    person_id: Unique identifier for the person assigned to the goal.
    person_number: Employee or person’s unique number in the system.
    assignment_id: Identifier for the goal’s assignment instance.
    description: Brief description or details about the goal.
    start_date: Date when the goal starts or becomes active.
    status: Current status of the goal (e.g., In Progress, Completed).
    target_completion_date: Intended date for goal completion.
    status_meaning: Descriptive meaning of the current status.
    percent_complete: Percentage indicating the progress of the goal.    

    
JRN_journey schema:
    - `journey_name`: The title or name of the journey (e.g., "Badge Request").
    - `category`: The category or type of the journey (e.g., "Badge_R").
    
    - `users`: A list of users associated with the journey. For each user, the following fields are included:
        - `person_name`: The name of the person participating in the journey.
        - `status`: The current status of the person in the journey (e.g., "In Progress", "Completed").
 
        - `tasks`: A list of tasks assigned to the user as part of the journey. For each task, the following fields are included:
            - `task_name`: The name or title of the task (e.g., "Request a Badge").
            - `status`: The current status of the task (e.g., "Not Started", "In Progress").
            - `task_start_date`: The date when the task started.
            - `task_due_date`: The date by which the task is due.
 
 
JRN_task schema:
    task_name: The name of the task.
    task_type: The type of task (e.g., Process Automation).
    performer: The role responsible for completing the task (e.g., Manager, Employee).
    owner: The owner of the task.
    description: A description of the task.
    task_link: A link to the task.
    duration: The task's duration.
    time_unit: The unit of time for the task (e.g., days, hours).
 
ABS_daily_leave_details schema:
    person_name: Name of the person taking leave.
    leave_type: The type of leave (e.g., Study Leave, Sick Leave).
    date: The date when the leave occurred.
    days: Number of leave days taken.
 
ABS_leave_application schema:
    person_name: Name of the person applying for leave.
    leave_type: The type of leave requested (e.g., Sick Leave, Vacation).
    start_date: Start date of the leave period.
    end_date: End date of the leave period.
    duration: Total duration of the leave.
    status: The current status of the leave application (e.g., approval required, approved).
 
ABS_leave_balance schema:
    person_name: Name of the person for whom leave balance is being tracked.
    leave_type: The type of leave (e.g., Sick Leave, Study Leave).
    leave_balance: The remaining balance of leave days. 
 
Instructions:
- Analyze the user's prompt and select the appropriate field names from the provided schemas.
- If the user request is ambiguous or general (e.g., "Turnover report"), infer the most relevant fields.
- Provide the field names as a Python dictionary with schema names as keys, and a list of relevant field names as values.
- Map synonyms and related terms used by the user to the correct field name. For example:
    - "compensation" refers to "base_salary" and "compensation" fields.
    - "department" refers to "organization_unit" and "business_unit."
    - "demographics" refers to fields like "date_of_birth", "gender", "nationality."
-Always include person_name for all schema.
- Always narrow down the selection to the minimum required fields based on the query.
- If the user asks for common HR reports (e.g., headcount, diversity, compensation analysis, turnover), include typical fields for those report types even if the user doesn't specify them.
 
input:{user_prompt}
response: Provide the fields as a Python dictionary with collection names and field lists.
"""
 
# Create a LangChain prompt template
prompt_template = PromptTemplate(input_variables=["user_prompt"], template=base_prompt)
 
# Function to get the raw response from the LLM
def get_raw_response(user_prompt):
    # Setup the LLMChain with the prompt template and the OpenAI model
    llm_chain = LLMChain(llm=OPENAI_LLM, prompt=prompt_template)
    
    # Run the chain and return the AI agent's raw response
    response = llm_chain.run({"user_prompt": user_prompt})
    return response
 
# Function to format the response into a dictionary with schema names
def format_response_as_dictionary(response):
    # Clean the response and convert it to a valid Python dictionary
    try:
        # Remove any extraneous text like ```python ... ```
        code_match = re.search(r"```python(.*?)```", response, re.DOTALL)
        if code_match:
            response = code_match.group(1).strip()  # Extract the inner code block
 
        # Use ast.literal_eval to safely evaluate the string as a Python dictionary
        fields_by_schema = ast.literal_eval(response)
        
        if isinstance(fields_by_schema, dict):
            print("Formatted response:", fields_by_schema)
            return fields_by_schema
        else:
            raise ValueError("Response is not a valid dictionary")
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing AI response: {e}")
        return {}
 
# Main function to generate and format report fields
def generate_graph_fields(user_prompt):
    # Get the raw response from the LLM
    raw_response = get_raw_response(user_prompt)
    print("*"*25)
    print("raw_response : ",raw_response)
    # Format the response into a dictionary
    formatted_response = format_response_as_dictionary(raw_response)
    
    return formatted_response

def generate_report3():
    user_description = "Generate a Gender Diversity report, broken down by department, without applying any filters, covering the current year."
    report_info = generate_graph_fields(user_description)
    
    # Fetch data from all three APIs
    employee_data = fetch_and_store_employee_data()
    salary_data = fetch_and_store_salary_data()
    worker_data = fetch_and_store_worker_data()

    combined_data = {}
    
    # Combine employee data using `person_number` and `assignment_id` as the key
    for emp in employee_data:
        person_name = emp.get('person_name')
        assignment_id = emp.get('assignment_id')
        # Use a string (person_number + assignment_id) as a unique key
        key = f"{person_name}_{assignment_id}" if person_name and assignment_id else person_name
        combined_data[key] = emp
    
    # Process the salary data
    for sal in salary_data:
        person_name = sal.get('person_name')
        assignment_id = sal.get('assignment_id')
        salary_effective_date = sal.get('salary_effective_date')
        
        # Ensure we have the person_number and assignment_id in the salary data
        if person_name and assignment_id:
            # Use the string (person_number + assignment_id) as a key
            key = f"{person_name}_{assignment_id}"
            
            # If the key exists in combined_data, update it
            if key in combined_data:
                # If there's already salary data, compare dates and keep the most recent one
                if 'salary_effective_date' in combined_data[key]:
                    existing_date_str = combined_data[key].get('salary_effective_date')
                    existing_date = datetime.strptime(existing_date_str, "%Y-%m-%d") if existing_date_str else None
                    new_date = datetime.strptime(salary_effective_date, "%Y-%m-%d")

                    # Only update if the new salary date is more recent
                    if existing_date is None or new_date > existing_date:
                        combined_data[key].update(sal)
                else:
                    # If there's no existing salary data, just add it
                    combined_data[key].update(sal)
            else:
                # If the key doesn't exist in combined_data, create a new entry with the salary data
                combined_data[key] = sal
    
    # Convert combined_data to a list without using the combined keys
    final_data = list(combined_data.values())
    
    # Flatten the list of fields from all schemas in report_info
    all_fields = []
    for fields in report_info.values():
        all_fields.extend(fields)

    print(all_fields)    

    # Iterate through worker data
    for worker in worker_data:
        person_name = worker.get('person_name')
        
        # Check if this person_number exists in the combined data
        matching_keys = [key for key in combined_data.keys() if key.startswith(person_name)]
        
        if person_name and matching_keys:
            # Iterate through each assignment in the worker data
            for assignment in worker.get('assignments', []):
                assignment_id = assignment.get('assignment_id')
                # Create a key to check in combined_data
                key = f"{person_name}_{assignment_id}"
                if key in combined_data:
                    # Merge assignment data directly into the combined entry
                    combined_data[key].update(assignment)
            
            # Now, iterate through the matching keys in combined_data to update with worker-level data
            for key in matching_keys:
                # Update the existing combined entry with the remaining worker data (excluding assignments)
                combined_data[key].update({
                    k: v for k, v in worker.items() if k != 'assignments'
                })

    # Convert combined_data to a list without using the combined keys
    final_data = list(combined_data.values())

    # Prepare final data based on all fields from the flattened list
    final_data1 = []
    for combined_entry in final_data:  # Iterate directly over the list
        # Extract only the fields present in `all_fields` from `combined_entry`
        final_entry = {field: combined_entry.get(field) for field in all_fields}
        
        # Add the final entry if it has any relevant data (non-None values)
        if any(final_entry.values()):  # Only add if there's any non-None value
            final_data1.append(final_entry)
    
    with open("Full data.json", "w", encoding="utf-8") as file:    
         file.write(str(final_data1) + "\n")



@app.route('/uno', methods=['POST'])
def trigger_task_deadline_alerts():
    try:
        generate_report3()
        return jsonify({"message": "Task deadline alerts sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Global variable to store the fetched data
fetched_data_emp = []
data_fetched_emp = False  # Flag to track if the data has already been fetched

CONFIGURATION_MAPPING_EMP = {
    "salutation": "Salutation",
    "first_name": "FirstName",
    "middle_name": "MiddleName",
    "last_name": "LastName",
    "previous_last_name": "PreviousLastName",
    "name_suffix": "NameSuffix",
    "person_name": "DisplayName",
    "preferred_name": "PreferredName",
    "honors": "Honors",
    "correspondence_language": "CorrespondenceLanguage",
    "person_number": "PersonNumber",
    "work_phone_country_code": "WorkPhoneCountryCode",
    "work_phone_area_code": "WorkPhoneAreaCode",
    "work_phone_number": "WorkPhoneNumber",
    "work_phone_extension": "WorkPhoneExtension",
    "work_phone_legislation_code": "WorkPhoneLegislationCode",
    "work_fax_country_code": "WorkFaxCountryCode",
    "work_fax_area_code": "WorkFaxAreaCode",
    "work_fax_number": "WorkFaxNumber",
    "work_fax_extension": "WorkFaxExtension",
    "work_fax_legislation_code": "WorkFaxLegislationCode",
    "work_mobile_phone_country_code": "WorkMobilePhoneCountryCode",
    "work_mobile_phone_area_code": "WorkMobilePhoneAreaCode",
    "work_mobile_phone_number": "WorkMobilePhoneNumber",
    "work_mobile_phone_extension": "WorkMobilePhoneExtension",
    "work_mobile_phone_legislation_code": "WorkMobilePhoneLegislationCode",
    "home_phone_country_code": "HomePhoneCountryCode",
    "home_phone_area_code": "HomePhoneAreaCode",
    "home_phone_number": "HomePhoneNumber",
    "home_phone_extension": "HomePhoneExtension",
    "home_phone_legislation_code": "HomePhoneLegislationCode",
    "home_fax_country_code": "HomeFaxCountryCode",
    "home_fax_area_code": "HomeFaxAreaCode",
    "home_fax_number": "HomeFaxNumber",
    "home_fax_extension": "HomeFaxExtension",
    "home_fax_legislation_code": "HomeFaxLegislationCode",
    "email": "WorkEmail",
    "address_line1": "AddressLine1",
    "address_line2": "AddressLine2",
    "address_line3": "AddressLine3",
    "city": "City",
    "region": "Region",
    "region2": "Region2",
    "home_country": "Country",
    "postal_code": "PostalCode",
    "date_of_birth": "DateOfBirth",
    "ethnicity": "Ethnicity",
    "projected_termination_date": "ProjectedTerminationDate",
    "legal_entity_id": "LegalEntityId",
    "hire_date": "HireDate",
    "termination_date": "TerminationDate",
    "gender": "Gender",
    "marital_status": "MaritalStatus",
    "national_id_type": "NationalIdType",
    "national_id": "NationalId",
    "national_id_country": "NationalIdCountry",
    "national_id_expiration_date": "NationalIdExpirationDate",
    "national_id_place_of_issue": "NationalIdPlaceOfIssue",
    "person_id": "PersonId",
    "effective_start_date_e": "EffectiveStartDate",
    "user_name": "UserName",
    "citizenship_id": "CitizenshipId",
    "citizenship_status": "CitizenshipStatus",
    "citizenship_legislation_code": "CitizenshipLegislationCode",
    "citizenship_to_date": "CitizenshipToDate",
    "religion": "Religion",
    "religion_id": "ReligionId",
    "passport_issue_date": "PassportIssueDate",
    "passport_number": "PassportNumber",
    "passport_issuing_country": "PassportIssuingCountry",
    "passport_id": "PassportId",
    "passport_expiration_date": "PassportExpirationDate",
    "license_number": "LicenseNumber",
    "drivers_license_expiration_date": "DriversLicenseExpirationDate",
    "drivers_license_issuing_country": "DriversLicenseIssuingCountry",
    "drivers_license_id": "DriversLicenseId",
    "military_vet_status": "MilitaryVetStatus",
    "creation_date": "CreationDate",
    "last_update_date": "LastUpdateDate",
    "worker_type": "WorkerType",
    "direct_reports": "DirectReports",
    "person_dff": "PersonDFF",
    "photo": "Photo",
    "roles": "Roles",
    "visas": "Visas",
    "person_extra_information": "PersonExtraInformation"
    # "salutation_lov": "SalutationLOV",
    # "religion_lov": "ReligionLOV",
    # "legal_employer_lov": "LegalEmployerLOV",
    # "citizenship_legislation_code_lov": "CitizenshipLegislationCodeLOV",
    # "gender_lov": "GenderLOV",
    # "citizenship_status_lov": "CitizenshipStatusLOV",
    # "correspondence_language_lov": "CorrespondenceLanguageLOV",
    # "national_id_type_lov": "NationalIdTypeLOV",
    # "ethnicity_lov": "EthnicityLOV",
    # "military_vet_status_lov": "MilitaryVetStatusLOV",
    # "marital_status_lov": "MaritalStatusLOV"
}

CONFIGURATION_MAPPING_ASSIGNMENT = {
    "assignment_name": "AssignmentName",
    "person_type_id": "PersonTypeId",
    "proposed_person_type_id": "ProposedPersonTypeId",
    "projected_start_date": "ProjectedStartDate",
    "business_unit_id": "BusinessUnitId",
    "location_id": "LocationId",
    "job_id": "JobId",
    "grade_id": "GradeId",
    "department_id": "DepartmentId",
    "worker_category": "WorkerCategory",
    "assignment_category": "AssignmentCategory",
    "working_from_home": "WorkingAtHome",
    "working_as_manager": "WorkingAsManager",
    "salary_code": "SalaryCode",
    "working_hours": "WorkingHours",
    "frequency": "Frequency",
    "start_time": "StartTime",
    "end_time": "EndTime",
    "base_salary": "SalaryAmount",
    "salary_basis_id": "SalaryBasisId",
    "action_code": "ActionCode",
    "action_reason_code": "ActionReasonCode",
    "employment_status": "AssignmentStatus",
    "work_tax_address_id": "WorkTaxAddressId",
    "assignment_id": "AssignmentId",
    "effective_start_date": "EffectiveStartDate",
    "effective_end_date": "EffectiveEndDate",
    "position_id": "PositionId",
    "terms_effective_start_date": "TermsEffectiveStartDate",
    "manager_id": "ManagerId",
    "manager_assignment_id": "ManagerAssignmentId",
    "manager_type": "ManagerType",
    "assignment_number": "AssignmentNumber",
    "original_hire_date": "OriginalHireDate",
    "assignment_status_type_id": "AssignmentStatusTypeId",
    "primary_assignment_flag": "PrimaryAssignmentFlag",
    "probation_period_end_date": "ProbationPeriodEndDate",
    "probation_period_length": "ProbationPeriodLength",
    "probation_period_unit_of_measure": "ProbationPeriodUnitOfMeasure",
    "assignment_projected_end_date": "AssignmentProjectedEndDate",
    "actual_termination_date": "ActualTerminationDate",
    "legal_entity_id": "LegalEntityId",
    "primary_work_relation_flag": "PrimaryWorkRelationFlag",
    "primary_work_terms_flag": "PrimaryWorkTermsFlag",
    "creation_date": "CreationDate",
    "last_update_date": "LastUpdateDate",
    "period_of_service_id": "PeriodOfServiceId",
    "full_time_or_part_time": "FullPartTime",
    "regular_temporary": "RegularTemporary",
    "grade_ladder_id": "GradeLadderId",
    "default_expense_account": "DefaultExpenseAccount",
    "people_group": "PeopleGroup"
}

# Function to map employee data to configuration
def map_employee_data_to_configuration(data):
    mapped_data = {}
    # Map top-level employee fields
    for key, value in CONFIGURATION_MAPPING_EMP.items():
        mapped_data[key] = data.get(value, None)

    # Find the latest assignment based on EffectiveStartDate if present
    if 'assignments' in data and data['assignments']:
        latest_assignment = None
        latest_date = None
        
        for assignment in data['assignments']:
            effective_start_date_str = assignment.get("EffectiveStartDate")
            if effective_start_date_str:
                try:
                    effective_start_date = datetime.strptime(effective_start_date_str, "%Y-%m-%d")
                    
                    # Update the latest_assignment if this one has a more recent date
                    if latest_date is None or effective_start_date > latest_date:
                        latest_date = effective_start_date
                        latest_assignment = assignment
                except ValueError:
                    # Handle any potential date parsing errors gracefully
                    continue

        if latest_assignment:
            # Map the fields from the latest assignment and merge them into the top-level mapped_data dictionary
            mapped_assignment = {}
            for key, value in CONFIGURATION_MAPPING_ASSIGNMENT.items():
                mapped_assignment[key] = latest_assignment.get(value, None)
            mapped_data.update(mapped_assignment)

    return mapped_data

# Function to fetch and store employee data
def fetch_and_store_employee_data():
    global fetched_data_emp, data_fetched_emp  # Access global variables

    if data_fetched_emp:
        return fetched_data_emp  # Return data if already fetched

    total_data = []  # List to store all the employee data
    limit = 50  # Fetch 50 items at a time
    offsets = list(range(0, 1500, limit))

    # Function to fetch employee data with offset and limit
    def fetch_employee_data(offset, limit=50):
        username = 'Vishal.Meena@payrollcloudcorp.com'
        password = 'Welcome#12345'
        url = f'https://iaihgs-dev1.fa.ocs.oraclecloud.com/hcmRestApi/resources/11.13.18.05/emps?limit={limit}&offset={offset}&expand=all&onlyData=true'

        try:
            response = requests.get(url, auth=(username, password))
            response.raise_for_status()
            return response.json().get('items', [])
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    # Use ThreadPoolExecutor to fetch data in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(fetch_employee_data, offset, limit) for offset in offsets]

        for future in concurrent.futures.as_completed(futures):
            data = future.result()
            if isinstance(data, dict) and "error" in data:
                return {"error": f"Error fetching data: {data['error']}"}
            total_data.extend(data)

    # Map the fetched API data to configuration
    fetched_data_emp = [map_employee_data_to_configuration(item) for item in total_data]
    data_fetched_emp = True  # Mark the data as fetched

    return fetched_data_emp

# Global variable to store the fetched data
fetched_data = []
data_fetched = False  # Flag to track if the data has already been fetched

# Configuration mapping as before
CONFIGURATION_MAPPING = { 
    "assignment_id": "AssignmentId",
    "salary_id": "SalaryId",
    "salary_basis_id": "SalaryBasisId",
    "salary_frequency_code": "SalaryFrequencyCode",
    "salary_basis_type": "SalaryBasisType",
    "currency": "CurrencyCode",
    "salary_effective_date": "DateFrom",
    "date_to": "DateTo",
    "base_salary": "SalaryAmount",
    "adjustment_amount": "AdjustmentAmount",
    "adjustment_percentage": "AdjustmentPercentage",
    "annual_salary": "AnnualSalary",
    "annual_full_time_salary": "AnnualFullTimeSalary",
    "quartile": "Quartile",
    "quintile": "Quintile",
    "compa_ratio": "CompaRatio",
    "range_position": "RangePosition",
    "salary_range_minimum": "SalaryRangeMinimum",
    "salary_range_mid_point": "SalaryRangeMidPoint",
    "salary_range_maximum": "SalaryRangeMaximum",
    "search_date": "SearchDate",
    "frequency": "FrequencyName",
    "assignment_number": "AssignmentNumber",
    "person_name": "DisplayName",
    "action_id": "ActionId",
    "action_reason_id": "ActionReasonId",
    "action_code": "ActionCode",
    "action_reason_code": "ActionReasonCode",
    "action_reason": "ActionReason",
    "action_name": "ActionName",
    "salary_basis": "Code",
    "legal_employer": "LegalEmployerName",
    "grade_ladder_name": "GradeLadderName",
    "grade_code": "GradeName",
    "grade_step_name": "GradeStepName",
    "geography_name": "GeographyName",
    "geography_type_name": "GeographyTypeName",
    "grade_id": "GradeId",
    "last_update_date": "LastUpdateDate",
    "last_updated_by": "LastUpdatedBy",
    "created_by": "CreatedBy",
    "creation_date": "CreationDate",
    "fte": "FTEValue",
    "next_sal_review_date": "NextSalReviewDate",
    "assignment_type": "AssignmentType",
    "amount_decimal_precision": "AmountDecimalPrecision",
    "salary_amount_scale": "SalaryAmountScale",
    "amount_rounding_code": "AmountRoundingCode",
    "annual_rounding_code": "AnnualRoundingCode",
    "range_rounding_code": "RangeRoundingCode",
    "work_at_home": "WorkAtHome",
    "quartile_meaning": "QuartileMeaning",
    "quintile_meaning": "QuintileMeaning",
    "legislative_data_group_Id": "LegislativeDataGroupId",
    "has_future_salary": "hasFutureSalary",
    "multiple_components": "MultipleComponents",
    "component_usage": "ComponentUsage",
    "pending_transaction_exists": "PendingTransactionExists",
    "range_error_warning": "RangeErrorWarning",
    "payroll_factor": "PayrollFactor",
    "multiplier": "SalaryFactor",
    "payroll_frequency_code": "PayrollFrequencyCode",
    "person_id": "PersonId",
    "business_title": "BusinessTitle",
    "person_number": "PersonNumber",
    "person_name": "PersonDisplayName",
    "grade_code": "GradeCode",
    "salary_components": "salaryComponents",
    "salary_pay_rate_components": "salaryPayRateComponents",
    "salary_simple_components": "salarySimpleComponents"
}

# Function to map API data to configuration
def map_data_to_configuration(data):
    mapped_data = {}
    for key, value in CONFIGURATION_MAPPING.items():
        mapped_data[key] = data.get(value, None)
    return mapped_data

# Function to fetch and store salary data
def fetch_and_store_salary_data():
    global fetched_data, data_fetched  # Access global variables

    if data_fetched:
        return fetched_data  # Return data if already fetched

    total_data = []  # List to store all the salary data
    limit = 50  # Fetch 50 items at a time
    offsets = list(range(0, 5000, limit))

    # Function to fetch salary data with offset and limit
    def fetch_salary_data(offset, limit=50):
        username = 'Vishal.Meena@payrollcloudcorp.com'
        password = 'Welcome#12345'
        url = f'https://iaihgs-dev1.fa.ocs.oraclecloud.com/hcmRestApi/resources/11.13.18.05/salaries?limit={limit}&offset={offset}&expand=all&onlyData=true'

        try:
            response = requests.get(url, auth=(username, password))
            response.raise_for_status()
            return response.json().get('items', [])
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    # Use ThreadPoolExecutor to fetch data in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(fetch_salary_data, offset, limit) for offset in offsets]

        for future in concurrent.futures.as_completed(futures):
            data = future.result()
            if isinstance(data, dict) and "error" in data:
                return {"error": f"Error fetching data: {data['error']}"}
            total_data.extend(data)

    # Map the fetched API data to configuration
    fetched_data = [map_data_to_configuration(item) for item in total_data]
    data_fetched = True  # Mark the data as fetched

    return fetched_data

# Global variable to store the fetched data
fetched_data_workers = []
data_fetched_workers = False  # Flag to track if the data has already been fetched

# Configuration mapping for public workers
CONFIGURATION_MAPPING_WORKERS = {
    "person_id": "PersonId",
    "person_number": "PersonNumber",
    "last_name": "LastName",
    "first_name": "FirstName",
    "title": "Title",
    "pre_name_adjunct": "PreNameAdjunct",
    "suffix": "Suffix",
    "middle_names": "MiddleNames",
    "honors": "Honors",
    "known_as": "KnownAs",
    "person_name": "DisplayName",
    "list_name": "ListName",
    "order_name": "OrderName",
    "email": "WorkEmail",
    "username": "Username"
}

CONFIGURATION_MAPPING_ASSIGNMENTSp = {
    "assignment_id": "AssignmentId",
    "assignment_number": "AssignmentNumber",
    "assignment_name": "AssignmentName",
    "legal_employer_name": "LegalEmployerName",
    "start_date": "StartDate",
    "primary_flag": "PrimaryFlag",
    "primary_assignment_flag": "PrimaryAssignmentFlag",
    "worker_type": "WorkerType",
    "worker_number": "WorkerNumber",
    "work_at_home_flag": "WorkAtHomeFlag",
    "full_part_time": "FullPartTime",
    "manager_name": "ManagerName",
    "business_unit": "BusinessUnitName",
    "department": "DepartmentName",
    "job_code": "JobCode",
    "job": "JobName",
    "position_code": "PositionCode",
    "position": "PositionName",
    "location_code": "LocationCode",
    "location": "LocationName",
    "grade_code": "GradeCode",
    "grade": "GradeName"
}

# Function to map API data to configuration
def map_worker_data_to_configuration(data):
    mapped_data = {}
    
    # Map the person-related attributes
    for key, value in CONFIGURATION_MAPPING_WORKERS.items():
        mapped_data[key] = data.get(value, None)
    
    # Process all assignments if present
    if 'assignments' in data and data['assignments']:
        mapped_data['assignments'] = []
        for assignment in data['assignments']:
            assignment_data = {}
            for key, value in CONFIGURATION_MAPPING_ASSIGNMENTSp.items():
                assignment_data[key] = assignment.get(value, None)
            mapped_data['assignments'].append(assignment_data)
    
    return mapped_data

# Function to fetch and store public worker data
def fetch_and_store_worker_data():
    global fetched_data_workers, data_fetched_workers  # Access global variables

    if data_fetched_workers:
        return fetched_data_workers  # Return data if already fetched

    total_data = []  # List to store all the worker data
    limit = 50  # Fetch 50 items at a time
    offsets = list(range(0, 5000, limit))

    # Function to fetch worker data with offset and limit
    def fetch_worker_data(offset, limit=50):
        username = 'Vishal.Meena@payrollcloudcorp.com'
        password = 'Welcome#12345'
        url = f'https://iaihgs-dev1.fa.ocs.oraclecloud.com/hcmRestApi/resources/11.13.18.05/publicWorkers?limit={limit}&offset={offset}&expand=all&onlyData=true'

        try:
            response = requests.get(url, auth=(username, password))
            response.raise_for_status()
            return response.json().get('items', [])
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    # Use ThreadPoolExecutor to fetch data in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(fetch_worker_data, offset, limit) for offset in offsets]

        for future in concurrent.futures.as_completed(futures):
            data = future.result()
            if isinstance(data, dict) and "error" in data:
                return {"error": f"Error fetching data: {data['error']}"}
            total_data.extend(data)

    # Map the fetched API data to configuration
    fetched_data_workers = [map_worker_data_to_configuration(item) for item in total_data]
    data_fetched_workers = True  # Mark the data as fetched

    return fetched_data_workers

if __name__ == '__main__':
    app.run(debug=True)
