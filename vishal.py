from flask import Flask, jsonify, request
import requests
import json
import concurrent.futures  # For parallel computing
 
app = Flask(__name__)
 
# Configuration mapping as given in the input
CONFIGURATION_MAPPING = {
    "assignment_id": "AssignmentId",
    "salary_id": "SalaryId",
    "salary_basis_id": "SalaryBasisId",
    "salary_frequency_code": "SalaryFrequencyCode",
    "salary_basis_type": "SalaryBasisType",
    "currency": "CurrencyCode",
    "Salary_effective_date": "DateFrom",
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
    "display_name": "DisplayName",
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
    "grade_code": "GradeCode"
}


CONFIGURATION_MAPPING2 = {
    "assignment_id": "AssignmentId",
    "salary_id": "SalaryId",
    "salary_basis_id": "SalaryBasisId",
    "salary_frequency_code": "SalaryFrequencyCode",
    "salary_basis_type": "SalaryBasisType",
    "currency": "CurrencyCode",
    "Salary_effective_date": "DateFrom",
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
    "display_name": "DisplayName",
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
    
    # Assignment-specific fields to be merged into the root
    "assignment_name": "AssignmentName",
    "person_type_id": "PersonTypeId",
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
    "assignment_status": "AssignmentStatus",
    "assignment_number": "AssignmentNumber",
    "legal_entity_id": "LegalEntityId",
    "full_part_time": "FullPartTime",
    "regular_temporary": "RegularTemporary"
}



# Function to map API data to configuration
def map_data_to_configuration(data):
    mapped_data = {}
    for key, value in CONFIGURATION_MAPPING.items():
        mapped_data[key] = data.get(value, None)  # Map API response to configuration keys
    return mapped_data

# Function to fetch salary data with offset and limit
def fetch_salary_data(offset, limit=50):
    username = 'Vishal.Meena@payrollcloudcorp.com'
    password = 'Welcome#12345'
    url = f'https://iaihgs-dev1.fa.ocs.oraclecloud.com/hcmRestApi/resources/11.13.18.05/salaries?limit={limit}&offset={offset}'
    
    try:
        response = requests.get(url, auth=(username, password))
        response.raise_for_status()  # Check if the request was successful
        return response.json().get('items', [])  # Return the 'items' list from the response
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Helper function to fetch data in parallel
def fetch_data_parallel(offsets, limit=50):
    total_data = []  # Store all data here

    # Use ThreadPoolExecutor to parallelize the requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # Schedule the execution of fetch_salary_data for each offset
        futures = {executor.submit(fetch_salary_data, offset, limit): offset for offset in offsets}
        
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

# API route to fetch salary data
@app.route('/api/salary_data', methods=['GET'])
def get_salary_data():
    total_data = []  # List to store all the salary data
    limit = 50  # Fetch 50 items at a time

    # Generate the offsets for fetching data (up to 1000 items with a limit of 50, in chunks)
    offsets = list(range(0, 1500, limit))

    # Fetch data using parallel threads
    raw_data = fetch_data_parallel(offsets, limit=limit)

    # If there's an error in the raw data fetching
    if isinstance(raw_data, dict) and "error" in raw_data:
        return jsonify(raw_data), 500

    # Map the raw API response data to the configuration
    mapped_data = [map_data_to_configuration(item) for item in raw_data]
    total_data.extend(mapped_data)  # Add the mapped data to the total list

    return jsonify(total_data), 200  # Return aggregated data as JSON

if __name__ == "__main__":
    app.run(debug=True)


#             "salutation": "Salutation",
#             "first_name": "FirstName",
#             "middle_name": "MiddleName",
#             "last_name": "LastName",
#             "previous_last_name": "PreviousLastName",
#             "name_suffix": "NameSuffix",
#             "person_name": "DisplayName",
#             "preferred_name": "PreferredName",
#             "honors": "Honors",
#             "correspondence_language": "CorrespondenceLanguage",
#             "person_number": "PersonNumber",
#             "work_phone_country_code": "WorkPhoneCountryCode",
#             "work_phone_area_code": "WorkPhoneAreaCode",
#             "phone_number": "WorkPhoneNumber",
#            "work_phone_extension": "WorkPhoneExtension",
#     "work_legislation_code": "WorkPhoneLegislationCode",
#     "work_fax_country_code": "WorkFaxCountryCode",
#     "work_fax_area_code": "WorkFaxAreaCode",
#     "work_fax_number": "WorkFaxNumber",
#     "work_fax_extension": "WorkFaxExtension",
#     "work_fax_legislation_code": "WorkFaxLegislationCode",
#     "work_mobile_phone_country_code": "WorkMobilePhoneCountryCode",
#     "work_mobile_phone_area_code": "WorkMobilePhoneAreaCode",
#     "work_mobile_phone_number": "WorkMobilePhoneNumber",
#     "work_mobile_phone_extension": "WorkMobilePhoneExtension",
#     "work_mobile_phone_legislation_code": "WorkMobilePhoneLegislationCode",
#     "home_phone_country_code": "HomePhoneCountryCode",
#     "home_phone_area_code": "HomePhoneAreaCode",
#     "home_phone_number": "HomePhoneNumber",
#     "home_phone_extension": "HomePhoneExtension",
#     "home_phone_legislation_code": "HomePhoneLegislationCode",
#     "home_fax_country_code": "HomeFaxCountryCode",
#     "home_fax_area_code": "HomeFaxAreaCode",
#     "home_fax_number": "HomeFaxNumber",
#     "home_fax_extension": "HomeFaxExtension",
#     "email": "WorkEmail",
#     "home_fax_legislation_code": "HomeFaxLegislationCode",
#     "address_line1": "AddressLine1",
#     "address_line2": "AddressLine2",
#     "address_line3": "AddressLine3",
#     "location": "City",
#     "region": "Region",
#     "region2": "Region2",
#     "country": "Country",
#     "postal_code": "PostalCode",
#     "date_of_birth": "DateOfBirth",
#     "ethnicity": "Ethnicity",
#     "effective_end_date": "ProjectedTerminationDate",
#     "legal_entity_id": "LegalEntityId",
#     "hire_date": "HireDate",*
#     "termination_date": "TerminationDate",*
#     "gender": "Gender",
#     "marital_status": "MaritalStatus",
#     "national_id_type": "NationalIdType",
#     "national_id": "NationalId",
#     "national_id_country": "NationalIdCountry",
#     "national_id_expiration_date": "NationalIdExpirationDate",
#     "national_id_place_of_issue": "NationalIdPlaceOfIssue",
#     "person_id": "PersonId",
#     "effective_start_date": "EffectiveStartDate",
#     "user_name": "UserName",
#     "citizenship_id": "CitizenshipId",
#     "citizenship_status": "CitizenshipStatus",
#     "citizenship_legislation_code": "CitizenshipLegislationCode",
#     "citizenship_to_date": "CitizenshipToDate",
#     "religion": "Religion",
#     "religion_id": "ReligionId",
#     "passport_issue_date": "PassportIssueDate",
#     "passport_number": "PassportNumber",
#     "passport_issuing_country": "PassportIssuingCountry",
#     "passport_id": "PassportId",
#     "passport_expiration_date": "PassportExpirationDate",
#     "license_number": "LicenseNumber",
#     "drivers_license_expiration_date": "DriversLicenseExpirationDate",
#     "drivers_license_issuing_country": "DriversLicenseIssuingCountry",
#     "drivers_license_id": "DriversLicenseId",
#     "military_vet_status": "MilitaryVetStatus",
#     "creation_date": "CreationDate",
#     "last_update_date": "LastUpdateDate",
#     "worker_type": "WorkerType"
# }