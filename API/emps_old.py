from datetime import datetime
import requests
import concurrent.futures
from flask import Flask, jsonify
from pymongo import MongoClient
import json
import re

# Flask App initialization
app = Flask(__name__)

# Load configuration file
with open("config.json", "r") as config_file:
    CONFIG = json.load(config_file)

# MongoDB Configuration
MONGODB_URI = CONFIG["mongodb"]["uri"]
DATABASE_NAME = CONFIG["mongodb"]["database_name"]
COLLECTION_NAME = CONFIG["mongodb"]["API_emps"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

CONFIGURATION_MAPPING_EMPS = {
    "national_id_country": "NationalIdCountry",
    "person_name": "DisplayName",
    "person_number": "PersonNumber",
    "hire_date": "HireDate",
    "home_country": "Country",
    "gender": "Gender",
    "citizenship_status": "CitizenshipStatus"
}

# Configurations
CONFIGURATION_MAPPING_EMP = {
    "person_number": "PersonNumber",
    "correspondence_language": "CorrespondenceLanguage",
    "blood_type": "BloodType",
    "date_of_birth": "DateOfBirth",
    "date_of_death": "DateOfDeath",
    "country_of_birth": "CountryOfBirth",
    "region_of_birth": "RegionOfBirth",
    "town_of_birth": "TownOfBirth"
}

CONFIGURATION_MAPPING_WORK_RELATIONSHIP = {
    "legislation_code": "LegislationCode",
    "legal_employer_name": "LegalEmployerName",
    "worker_type": "WorkerType",
    "start_date": "StartDate",
    "legal_employer_seniority_date": "LegalEmployerSeniorityDate",
    "enterprise_seniority_date": "EnterpriseSeniorityDate",
    "on_military_service_flag": "OnMilitaryServiceFlag",
    "worker_number": "WorkerNumber",
    "termination_date": "TerminationDate",
    "last_working_date": "LastWorkingDate",
    "recommended_for_rehire": "RecommendedForRehire",
    "recommendation_reason": "RecommendationReason",
    "recommendation_authorized_by_person_id": "RecommendationAuthorizedByPersonId",
    "projected_termination_date": "ProjectedTerminationDate"
}

CONFIGURATION_MAPPING_ASSIGNMENTS = {
    "assignment_number": "AssignmentNumber",
    "assignment_name": "AssignmentName",
    "action_code": "ActionCode",
    "reason_code": "ReasonCode",
    "effective_start_date": "EffectiveStartDate",
    "effective_end_date": "EffectiveEndDate",
    "effective_sequence": "EffectiveSequence",
    "effective_latest_change": "EffectiveLatestChange",
    "business_unit": "BusinessUnitName",
    "assignment_type": "AssignmentType",
    "assignment_status_type_code": "AssignmentStatusTypeCode",
    "assignment_status_type": "AssignmentStatusType",
    "system_person_type": "SystemPersonType",
    "user_person_type": "UserPersonType",
    "proposed_user_person_type": "ProposedUserPersonType",
    "projected_start_date": "ProjectedStartDate",
    "projected_end_date": "ProjectedEndDate",
    "primary_assignment_flag": "PrimaryAssignmentFlag",
    "position_code": "PositionCode",
    "synchronize_from_position_flag": "SynchronizeFromPositionFlag",
    "job_code": "JobCode",
    "grade_code": "GradeCode",
    "grade_ladder_name": "GradeLadderName",
    "grade_step_eligibility_flag": "GradeStepEligibilityFlag",
    "grade_ceiling_step_id": "GradeCeilingStepId",
    "grade_ceiling_step": "GradeCeilingStep",
    "department": "DepartmentName",
    "reporting_establishment_name": "ReportingEstablishmentName",
    "location_code": "LocationCode",
    "working_from_home": "WorkAtHomeFlag",
    "assignment_category": "AssignmentCategory",
    "worker_category_code": "WorkerCategory",
    "permanent_temporary": "PermanentTemporary",
    "full_time_or_part_time": "FullPartTime",
    "working_as_manager": "ManagerFlag",
    "hourly_salaried_code": "HourlySalariedCode",
    "NormalHours": "NormalHours",
    "frequency": "Frequency",
    "start_time": "StartTime",
    "end_time": "EndTime",
    "seniority_basis": "SeniorityBasis",
    "probation_period": "ProbationPeriod",
    "probation_period_unit": "ProbationPeriodUnit",
    "probation_end_date": "ProbationEndDate",
    "notice_period": "NoticePeriod",
    "notice_period_uom": "NoticePeriodUOM",
    "expense_check_send_to_address": "ExpenseCheckSendToAddress",
    "retirement_age": "RetirementAge",
    "retirement_date": "RetirementDate",
    "labour_union_member_flag": "LabourUnionMemberFlag",
    "union_name": "UnionName",
    "bargaining_unit_code": "BargainingUnitCode",
    "collective_agreement_name": "CollectiveAgreementName",
    "contract_number": "ContractNumber",
    "internal_building": "InternalBuilding",
    "internal_floor": "InternalFloor",
    "internal_office_number": "InternalOfficeNumber",
    "internal_mailstop": "InternalMailstop",
    "default_expense_account": "DefaultExpenseAccount",
    "people_group": "PeopleGroup",
    "standard_working_hours": "StandardWorkingHours",
    "standard_frequency": "StandardFrequency"
}

# Function to map EMP data
def map_emp_data(emp_item):
    return {key: emp_item.get(value, None) for key, value in CONFIGURATION_MAPPING_EMPS.items()}

def map_employee_data(data):
    """
    Map the employee data to the configuration.
    """
    return {key: data.get(value, None) for key, value in CONFIGURATION_MAPPING_EMP.items()}

def map_work_relationship_data(data):
    """
    Map the work relationship data to the configuration.
    """
    return {key: data.get(value, None) for key, value in CONFIGURATION_MAPPING_WORK_RELATIONSHIP.items()}

def map_assignment_data(data):
    """
    Map the assignment data and fetch the one with the latest EffectiveStartDate.
    """
    latest_assignment = None
    latest_work_relationship = None
    latest_start_date = datetime.min
    
    for work_relationship in data.get("workRelationships", []):
        for assignment in work_relationship.get("assignments", []):
            start_date_str = assignment.get("EffectiveStartDate")
            print(start_date_str)
            print(latest_start_date)
            if start_date_str:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                if start_date > latest_start_date:
                    latest_start_date = start_date
                    latest_work_relationship = work_relationship
                    latest_assignment = assignment

    # Map work relationship data
    if latest_assignment and latest_work_relationship:
        work_relationship_data = map_work_relationship_data(latest_work_relationship)
        assignment_data = {key: latest_assignment.get(value, None) for key, value in CONFIGURATION_MAPPING_ASSIGNMENTS.items()}
        
        # Combine work relationship data and assignment data
        return {**work_relationship_data, **assignment_data}
    
    return None

# Fetch EMP data from Oracle HCM API
def fetch_emps_data():
    emps_data = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_emp_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/emps?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_emp_chunk, offset) for offset in offsets]):
            emps_data.extend(future.result())

    return [map_emp_data(emp) for emp in emps_data]

def fetch_workers_with_assignments():
    """
    Fetch workers data with expanded workRelationships and assignments.
    """
    total_data = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_worker_data(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/workers?limit={api_config['limit']}&offset={offset}&expand=workRelationships.assignments"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get("items", [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_worker_data, offset) for offset in offsets]):
            total_data.extend(future.result())

    return total_data

# Main report generation
def generate_report3():
    # Fetch and process workers data
    try:
        workers_data = fetch_workers_with_assignments()
        emps_data = fetch_emps_data()

        # Dictionary for quick lookup of EMP data by person_number
        emp_data_lookup = {emp["person_number"]: emp for emp in emps_data}

        combined_data = []

        for item in workers_data:
            # Map and process employee data
            employee_data = map_employee_data(item)
            
            # Add EMP data if available
            emp_details = emp_data_lookup.get(employee_data.get("person_number"), {})
            employee_data.update(emp_details)

            # for work_relationship in item.get("workRelationships", []):
            #     # Map work relationship data
            work_relationship=item.get("workRelationships", [])   
        
            
            # Map the latest assignment
            latest_assignment = map_assignment_data({"workRelationships": work_relationship})
            
            # Create a flattened document with employee, work_relationship, and latest_assignment
            combined_data.append({
                **employee_data,  # Flatten employee data
                 # Flatten work relationship data
                **latest_assignment  # Add latest assignment
            })

       
          # Insert combined data into MongoDB
        if combined_data:
            collection.insert_many(combined_data)
            print(f"Inserted {len(combined_data)} records successfully.")


    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")





    
