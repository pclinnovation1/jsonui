import requests
import concurrent.futures

# Global variable to store the fetched data
fetched_data = []
data_fetched = False  # Flag to track if the data has already been fetched

CONFIGURATION_MAPPING_EMP = {
    "person_id": "PersonId",
    "person_number": "PersonNumber",
    "correspondence_language": "CorrespondenceLanguage",
    "blood_type": "BloodType",
    "date_of_birth": "DateOfBirth",
    "date_of_death": "DateOfDeath",
    "country_of_birth": "CountryOfBirth",
    "region_of_birth": "RegionOfBirth",
    "town_of_birth": "TownOfBirth",
    "applicant_number": "ApplicantNumber",
    "created_by": "CreatedBy",
    "creation_date": "CreationDate",
    "last_updated_by": "LastUpdatedBy",
    "last_update_date": "LastUpdateDate",
    "driver_licenses": "driverLicenses",
    "visas_permits": "visasPermits",
    "photos": "Photos",
    "religions": "Religions",
    "ethnicities": "Ethnicities",
    "external_identifiers": "ExternalIdentifiers",
    "other_communication_accounts": "otherCommunicationAccounts",
    "passports": "passports",
    "disabilities": "Disabilities",
    "messages": "Messages"
}

CONFIGURATION_MAPPING_WORKERS_EFF = {
    "person_id": "PersonId",
    "category_code": "CategoryCode"
}

CONFIGURATION_MAPPING_WORKERS_DFF = {
    "person_id": "PersonId",
    "occupational_healthcare1": "occupationalHealthcare1",
    "occupational_healthcare2": "occupationalHealthcare2",
    "residence_permit_type": "residencePermitType",
    "a1_certification_valid_until": "a1CertificationValidUntil",
    "health_insurance_company": "healthInsuranceCompany",
    "flex_context": "__FLEX_Context"
}

CONFIGURATION_MAPPING_ADDRESSES = {
    "address_id": "AddressId",
    "effective_start_date": "EffectiveStartDate",
    "effective_end_date": "EffectiveEndDate",
    "address_line1": "AddressLine1",
    "address_line2": "AddressLine2",
    "address_line3": "AddressLine3",
    "address_line4": "AddressLine4",
    "town_or_city": "TownOrCity",
    "region1": "Region1",
    "region2": "Region2",
    "region3": "Region3",
    "country": "Country",
    "postal_code": "PostalCode",
    "long_postal_code": "LongPostalCode",
    "addl_address_attribute1": "AddlAddressAttribute1",
    "addl_address_attribute2": "AddlAddressAttribute2",
    "addl_address_attribute3": "AddlAddressAttribute3",
    "addl_address_attribute4": "AddlAddressAttribute4",
    "addl_address_attribute5": "AddlAddressAttribute5",
    "building": "Building",
    "floor_number": "FloorNumber",
    "created_by": "CreatedBy",
    "creation_date": "CreationDate",
    "last_updated_by": "LastUpdatedBy",
    "last_update_date": "LastUpdateDate",
    "person_addr_usage_id": "PersonAddrUsageId",
    "address_type": "AddressType",
    "validation_status_code": "ValidationStatusCode",
    "provider": "Provider",
    "longitude": "Longitude",
    "latitude": "Latitude",
    "primary_flag": "PrimaryFlag"
}

CONFIGURATION_MAPPING_CITIZENSHIP = {
    "citizenship_id": "CitizenshipId",
    "citizenship": "Citizenship",
    "from_date": "FromDate",
    "to_date": "ToDate",
    "citizenship_status": "CitizenshipStatus",
    "created_by": "CreatedBy",
    "creation_date": "CreationDate",
    "last_updated_by": "LastUpdatedBy",
    "last_update_date": "LastUpdateDate"
}

CONFIGURATION_MAPPING_EMAILS = {
    "email_address_id": "EmailAddressId",
    "email_type": "EmailType",
    "email_address": "EmailAddress",
    "from_date": "FromDate",
    "to_date": "ToDate",
    "created_by": "CreatedBy",
    "creation_date": "CreationDate",
    "last_updated_by": "LastUpdatedBy",
    "last_update_date": "LastUpdateDate",
    "primary_flag": "PrimaryFlag"
}

CONFIGURATION_MAPPING_LEGISLATIVE_INFO = {
    "person_legislative_id": "PersonLegislativeId",
    "effective_start_date": "EffectiveStartDate",
    "effective_end_date": "EffectiveEndDate",
    "legislation_code": "LegislationCode",
    "gender": "Gender",
    "marital_status": "MaritalStatus",
    "marital_status_change_date": "MaritalStatusChangeDate",
    "highest_education_level": "HighestEducationLevel",
    "created_by": "CreatedBy",
    "creation_date": "CreationDate",
    "last_updated_by": "LastUpdatedBy",
    "last_update_date": "LastUpdateDate"
}

CONFIGURATION_MAPPING_NAMES = {
    "person_name_id": "PersonNameId",
    "effective_start_date": "EffectiveStartDate",
    "effective_end_date": "EffectiveEndDate",
    "legislation_code": "LegislationCode",
    "last_name": "LastName",
    "first_name": "FirstName",
    "title": "Title",
    "pre_name_adjunct": "PreNameAdjunct",
    "suffix": "Suffix",
    "middle_names": "MiddleNames",
    "honors": "Honors",
    "known_as": "KnownAs",
    "previous_last_name": "PreviousLastName",
    "display_name": "DisplayName",
    "order_name": "OrderName",
    "list_name": "ListName",
    "full_name": "FullName",
    "military_rank": "MilitaryRank",
    "name_language": "NameLanguage",
    "name_information1": "NameInformation1",
    "name_information2": "NameInformation2",
    "name_information3": "NameInformation3",
    "name_information4": "NameInformation4",
    "name_information5": "NameInformation5",
    "name_information6": "NameInformation6",
    "name_information7": "NameInformation7",
    "name_information8": "NameInformation8",
    "name_information9": "NameInformation9",
    "name_information10": "NameInformation10",
    "created_by": "CreatedBy",
    "creation_date": "CreationDate",
    "last_updated_by": "LastUpdatedBy",
    "last_update_date": "LastUpdateDate",
    "local_person_name_id": "LocalPersonNameId",
    "local_effective_start_date": "LocalEffectiveStartDate",
    "local_effective_end_date": "LocalEffectiveEndDate",
    "local_legislation_code": "LocalLegislationCode",
    "local_last_name": "LocalLastName",
    "local_first_name": "LocalFirstName",
    "local_title": "LocalTitle",
    "local_pre_name_adjunct": "LocalPreNameAdjunct",
    "local_suffix": "LocalSuffix",
    "local_middle_names": "LocalMiddleNames",
    "local_honors": "LocalHonors",
    "local_known_as": "LocalKnownAs",
    "local_previous_last_name": "LocalPreviousLastName",
    "local_display_name": "LocalDisplayName",
    "local_order_name": "LocalOrderName",
    "local_list_name": "LocalListName",
    "local_full_name": "LocalFullName",
    "local_military_rank": "LocalMilitaryRank",
    "local_name_language": "LocalNameLanguage"
}

CONFIGURATION_MAPPING_NATIONAL_IDENTIFIERS = {
    "national_identifier_id": "NationalIdentifierId",
    "legislation_code": "LegislationCode",
    "national_identifier_type": "NationalIdentifierType",
    "national_identifier_number": "NationalIdentifierNumber",
    "issue_date": "IssueDate",
    "expiration_date": "ExpirationDate",
    "place_of_issue": "PlaceOfIssue",
    "created_by": "CreatedBy",
    "creation_date": "CreationDate",
    "last_updated_by": "LastUpdatedBy",
    "last_update_date": "LastUpdateDate",
    "primary_flag": "PrimaryFlag"
}

CONFIGURATION_MAPPING_PHONES = {
    "phone_id": "PhoneId",
    "phone_type": "PhoneType",
    "legislation_code": "LegislationCode",
    "country_code_number": "CountryCodeNumber",
    "area_code": "AreaCode",
    "phone_number": "PhoneNumber",
    "extension": "Extension",
    "from_date": "FromDate",
    "to_date": "ToDate",
    "validity": "Validity",
    "created_by": "CreatedBy",
    "creation_date": "CreationDate",
    "last_updated_by": "LastUpdatedBy",
    "last_update_date": "LastUpdateDate",
    "primary_flag": "PrimaryFlag"
}

CONFIGURATION_MAPPING_WORK_RELATIONSHIPS = {
    "period_of_service_id": "PeriodOfServiceId",
    "legislation_code": "LegislationCode",
    "legal_entity_id": "LegalEntityId",
    "legal_employer_name": "LegalEmployerName",
    "worker_type": "WorkerType",
    "primary_flag": "PrimaryFlag",
    "start_date": "StartDate",
    "legal_employer_seniority_date": "LegalEmployerSeniorityDate",
    "enterprise_seniority_date": "EnterpriseSeniorityDate",
    "on_military_service_flag": "OnMilitaryServiceFlag",
    "worker_number": "WorkerNumber",
    "ready_to_convert_flag": "ReadyToConvertFlag",
    "termination_date": "TerminationDate",
    "notification_date": "NotificationDate",
    "last_working_date": "LastWorkingDate",
    "revoke_user_access": "RevokeUserAccess",
    "recommended_for_rehire": "RecommendedForRehire",
    "recommendation_reason": "RecommendationReason",
    "recommendation_authorized_by_person_id": "RecommendationAuthorizedByPersonId",
    "created_by": "CreatedBy",
    "creation_date": "CreationDate",
    "last_updated_by": "LastUpdatedBy",
    "last_update_date": "LastUpdateDate",
    "projected_termination_date": "ProjectedTerminationDate"
}

# Function to map API data to the correct configuration
def map_data_to_configuration(data, configuration_mapping):
    mapped_data = {}
    for key, value in configuration_mapping.items():
        mapped_data[key] = data.get(value, None)
    return mapped_data

# Function to fetch and store worker data
def fetch_and_store_worker_data():
    global fetched_data, data_fetched  # Access global variables

    if data_fetched:
        return fetched_data  # Return data if already fetched

    total_data = []  # List to store all worker data
    limit = 50  # Fetch 50 items at a time
    offsets = list(range(0, 3000, limit))  # Adjust the range as necessary

    # Function to fetch worker data with offset and limit
    def fetch_worker_data(offset, limit=50):
        username = 'Vishal.Meena@payrollcloudcorp.com'
        password = 'Welcome#12345'
        url = f'https://iaihgs-dev1.fa.ocs.oraclecloud.com:443/hcmRestApi/resources/11.13.18.05/workers?limit={limit}&offset={offset}&expand=all'

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

    # Map the fetched API data to the appropriate configuration
    fetched_data = [map_data_to_configuration(item, CONFIGURATION_MAPPING_EMP) for item in total_data]
    data_fetched = True  # Mark the data as fetched

    return fetched_data

# Function to query the fetched worker data and select specific fields
def query_worker_data(query_params=None, select_fields=None):
    global fetched_data
    filtered_data = fetched_data  # Use the fetched data

    # If query_params is provided, apply the filtering logic
    if query_params:
        for param, value in query_params.items():
            if value:  # Filter only if a value is provided
                filtered_data = [item for item in filtered_data if str(item.get(param, '')).lower() == str(value).lower()]

    # If select_fields is provided, return only the requested fields
    if select_fields:
        # Create a list of filtered data with only the specified fields
        filtered_data = [{field: item.get(field, None) for field in select_fields} for item in filtered_data]

    return filtered_data

# Function to clear the fetched data
def clear_fetched_data():
    global fetched_data, data_fetched
    fetched_data = []  # Clear the data
    data_fetched = False  # Reset the flag
    return "Data cleared successfully."

if __name__ == "__main__":
    # Fetch and store worker data
    data = fetch_and_store_worker_data()
    print("Data fetched successfully.")

    # Example 1: No query parameters, return all data with all fields
    filtered_data = query_worker_data()  # No query params, no specific fields
    print(f"Filtered Data (All Data): {filtered_data}")

    # Example 2: No query parameters, but select specific fields
    selected_fields = ['person_id', 'person_number']
    filtered_data = query_worker_data(select_fields=selected_fields)  # No query params, only specific fields
    print(f"Filtered Data (Selected Fields): {filtered_data}")

    # Example 3: Run a query and get all fields (no select_fields provided)
    query_params = {'person_id': '123'}
    filtered_data = query_worker_data(query_params)  # Query params provided, return all fields
    print(f"Filtered Data (With Query, All Fields): {filtered_data}")

    # Example 4: Run a query and get only specific fields
    filtered_data = query_worker_data(query_params, select_fields=selected_fields)
    print(f"Filtered Data (With Query and Selected Fields): {filtered_data}")

    # Clear the data after all queries are completed
    clear_fetched_data()
    print("Data cleared.")
