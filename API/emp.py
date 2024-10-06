import requests, json
import concurrent.futures

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
    "work_email": "WorkEmail",
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
    "direct_reports": "DirectReports",
    "person_dff": "PersonDFF",
    "photo": "Photo",
    "roles": "Roles",
    "visas": "Visas",
    "person_extra_information": "PersonExtraInformation",
    "salutation_lov": "SalutationLOV",
    "religion_lov": "ReligionLOV",
    "legal_employer_lov": "LegalEmployerLOV",
    "citizenship_legislation_code_lov": "CitizenshipLegislationCodeLOV",
    "gender_lov": "GenderLOV",
    "citizenship_status_lov": "CitizenshipStatusLOV",
    "correspondence_language_lov": "CorrespondenceLanguageLOV",
    "national_id_type_lov": "NationalIdTypeLOV",
    "ethnicity_lov": "EthnicityLOV",
    "military_vet_status_lov": "MilitaryVetStatusLOV",
    "marital_status_lov": "MaritalStatusLOV"
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
    "full_part_time": "FullPartTime",
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

    # Map all assignments if present
    if 'assignments' in data and data['assignments']:
        mapped_data['assignments'] = []
        for assignment in data['assignments']:
            mapped_assignment = {}
            for key, value in CONFIGURATION_MAPPING_ASSIGNMENT.items():
                mapped_assignment[key] = assignment.get(value, None)
            mapped_data['assignments'].append(mapped_assignment)
    else:
        mapped_data['assignments'] = []

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
        url = f'https://iaihgs-dev1.fa.ocs.oraclecloud.com/hcmRestApi/resources/11.13.18.05/emps?limit={limit}&offset={offset}&expand=all'

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

# Function to query the fetched employee data and select specific fields
def query_employee_data(query_params=None, select_fields=None):
    global fetched_data_emp
    filtered_data = fetched_data_emp  # Use the fetched data

    # If query_params is provided, apply the filtering logic
    if query_params:
        for param, value in query_params.items():
            if value:  # Filter only if a value is provided
                filtered_data = [item for item in filtered_data if str(item.get(param, '')).lower() == str(value).lower()]

    # If select_fields is provided, return only the requested fields
    if select_fields:
        filtered_data = [{field: item.get(field, None) for field in select_fields} for item in filtered_data]

    return filtered_data

# Function to clear the fetched employee data
def clear_fetched_employee_data():
    global fetched_data_emp, data_fetched_emp
    fetched_data_emp = []  # Clear the data
    data_fetched_emp = False  # Reset the flag
    return "Employee data cleared successfully."

if __name__ == "__main__":
   # Fetch and store employee data
    data_emp = fetch_and_store_employee_data()
    print("Employee Data fetched successfully.")

    # # Save all data to a JSON file
    # with open('data.json', 'w') as json_file:
    #     json.dump(data_emp, json_file, indent=4)

    # # Example 1: No query parameters, return all employee data with all fields
    # filtered_data_emp = query_employee_data()  # No query params, no specific fields
    # print(f"Filtered Employee Data (All Data): {filtered_data_emp}")

    # # Example 2: No query parameters, but select specific fields
    # selected_fields_emp = ['person_number', 'work_email']
    # filtered_data_emp = query_employee_data(select_fields=selected_fields_emp)  # No query params, only specific fields
    # print(f"Filtered Employee Data (Selected Fields): {filtered_data_emp}")

    # # Example 3: Query with specific parameters (e.g., filter by `person_number`)
    # query_params_emp = {'person_number': 'FI7552'}
    # filtered_data_emp = query_employee_data(query_params=query_params_emp)
    # print(f"Filtered Employee Data (With Query): {filtered_data_emp}")

    # Example 4: Query with parameters and select specific fields
    selected_fields_emp = ['person_name', 'assignments']
    query_params_emp = {'person_number': 'FI7552'}
    filtered_data_emp = query_employee_data(query_params=query_params_emp, select_fields=selected_fields_emp)
    print(f"Filtered Employee Data (With Query and Selected Fields): {filtered_data_emp}")


    # Clear the data after all queries are completed
    clear_fetched_employee_data()
    print("Employee data cleared.")

