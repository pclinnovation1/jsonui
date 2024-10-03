from flask import Flask, jsonify, request
import requests
import json
import concurrent.futures  # For parallel computing

 
app = Flask(__name__)
CONFIGURATION_MAPPING_EMP = {
    # Employee-specific fields
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
    "work_email": "WorkEmail",
    "home_fax_legislation_code": "HomeFaxLegislationCode",
    "address_line1": "AddressLine1",
    "address_line2": "AddressLine2",
    "address_line3": "AddressLine3",
    "city": "City",
    "region": "Region",
    "region2": "Region2",
    "country": "Country",
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
    "effective_start_date": "EffectiveStartDate",
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
    
    # Assignment-specific fields (within 'assignments')
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
    "working_at_home": "WorkingAtHome",
    "working_as_manager": "WorkingAsManager",
    "salary_code": "SalaryCode",
    "working_hours": "WorkingHours",
    "frequency": "Frequency",
    "start_time": "StartTime",
    "end_time": "EndTime",
    "salary_amount": "SalaryAmount",
    "salary_basis_id": "SalaryBasisId",
    "action_code": "ActionCode",
    "action_reason_code": "ActionReasonCode",
    "assignment_status": "AssignmentStatus",
    "assignment_number": "AssignmentNumber",
    "legal_entity_id": "LegalEntityId",
    "effective_start_date_assignment": "EffectiveStartDate",  # Differentiating from person effective start
    "effective_end_date_assignment": "EffectiveEndDate",  # Assignment-specific effective end date
    "position_id": "PositionId",
    "terms_effective_start_date": "TermsEffectiveStartDate",
    "manager_id": "ManagerId",
    "manager_assignment_id": "ManagerAssignmentId",
    "manager_type": "ManagerType",
    "original_hire_date": "OriginalHireDate",
    "assignment_status_type_id": "AssignmentStatusTypeId",
    "primary_assignment_flag": "PrimaryAssignmentFlag",
    "probation_period_end_date": "ProbationPeriodEndDate",
    "probation_period_length": "ProbationPeriodLength",
    "probation_period_unit_of_measure": "ProbationPeriodUnitOfMeasure",
    "assignment_projected_end_date": "AssignmentProjectedEndDate",
    "actual_termination_date": "ActualTerminationDate",
    "primary_work_relation_flag": "PrimaryWorkRelationFlag",
    "primary_work_terms_flag": "PrimaryWorkTermsFlag",
    "period_of_service_id": "PeriodOfServiceId",
    "full_part_time": "FullPartTime",
    "regular_temporary": "RegularTemporary",
    "grade_ladder_id": "GradeLadderId",
    "default_expense_account": "DefaultExpenseAccount",
    "people_group": "PeopleGroup"
}

# Function to map employee data to configuration
def map_employee_data_to_configuration(data):
    mapped_data = {}
    # Map top-level fields
    for key, value in CONFIGURATION_MAPPING_EMP.items():
        if value in data:
            mapped_data[key] = data.get(value, None)
    
    # If assignments exist, map assignment-related fields
    if 'assignments' in data and data['assignments']:
        assignment = data['assignments'][0]  # Assuming we are interested in the first assignment
        for key, value in CONFIGURATION_MAPPING_EMP.items():
            if value in assignment:
                mapped_data[key] = assignment.get(value, None)
    return mapped_data

# Function to fetch employee data with offset and limit using requests
def fetch_employee_data(offset, limit=50):
    username = 'Vishal.Meena@payrollcloudcorp.com'
    password = 'Welcome#12345'
    url = f'https://iaihgs-dev1.fa.ocs.oraclecloud.com/hcmRestApi/resources/11.13.18.05/emps?limit={limit}&offset={offset}&expand=all'
    
    try:
        response = requests.get(url, auth=(username, password))
        response.raise_for_status()  # Check if the request was successful
        return response.json().get('items', [])  # Return the 'items' list from the response
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Helper function to fetch data in parallel using ThreadPoolExecutor
def fetch_data_parallel_emp(offsets, limit=50):
    total_data = []  # Store all data here

    # Use ThreadPoolExecutor to parallelize the requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # Schedule the execution of fetch_employee_data for each offset
        futures = {executor.submit(fetch_employee_data, offset, limit): offset for offset in offsets}
        
        
        for future in concurrent.futures.as_completed(futures):
            offset = futures[future]
            try:
                data = future.result()
                if isinstance(data, dict) and "error" in data:
                    return {"error": f"Error fetching data at offset {offset}: {data['error']}"}
                total_data.extend(data)  # Append the fetched data
            except Exception as e:
                return {"error": f"Exception at offset {offset}: {str(e)}"}

    return total_data

# API route to fetch employee data
@app.route('/api/emp_data', methods=['GET'])
def get_emp_data():
    total_data = []  # List to store all the employee data
    limit = 50  # Fetch 50 items at a time

    # Generate the offsets for fetching data (up to 1500 items with a limit of 50, in chunks)
    offsets = list(range(0, 1500, limit))
    
    # Fetch data using parallel threads
    raw_data = fetch_data_parallel_emp(offsets, limit=limit)

    # If there's an error in the raw data fetching
    if isinstance(raw_data, dict) and "error" in raw_data:
        return jsonify(raw_data), 500

    # Map the raw API response data to the configuration
    mapped_data = [map_employee_data_to_configuration(item) for item in raw_data]
    total_data.extend(mapped_data)  # Add the mapped data to the total list

    return jsonify(total_data), 200  # Return aggregated data as JSON


if __name__ == "__main__":
    app.run(debug=True)