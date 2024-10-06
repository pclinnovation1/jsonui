import requests,json
import concurrent.futures

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
    offsets = list(range(0, 3000, limit))

    # Function to fetch salary data with offset and limit
    def fetch_salary_data(offset, limit=50):
        username = 'Vishal.Meena@payrollcloudcorp.com'
        password = 'Welcome#12345'
        url = f'https://iaihgs-dev1.fa.ocs.oraclecloud.com/hcmRestApi/resources/11.13.18.05/salaries?limit={limit}&offset={offset}&expand=all'

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

# Function to query the fetched data and select specific fields
def query_salary_data(query_params=None, select_fields=None):
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
    # Fetch and store salary data
    data = fetch_and_store_salary_data()
    print("Data fetched successfully.")

    # Example 1: No query parameters, return all data with all fields
    filtered_data = query_salary_data()  # No query params, no specific fields
    print(f"Filtered Data (All Data): {filtered_data}")

    # Example 2: No query parameters, but select specific fields
    selected_fields = ['salary_components']
    filtered_data = query_salary_data(select_fields=selected_fields)  # No query params, only specific fields
    print(f"Filtered Data (Selected Fields): {filtered_data}")

    # # Example 3: Run a query and get all fields (no select_fields provided)
    # query_params = {'assignment_id': '123'}
    # filtered_data = query_salary_data(query_params)  # Query params provided, return all fields
    # print(f"Filtered Data (With Query, All Fields): {filtered_data}")

    # # Example 4: Run a query and get only specific fields
    # filtered_data = query_salary_data(query_params, select_fields=selected_fields)
    # print(f"Filtered Data (With Query and Selected Fields): {filtered_data}")

    # Clear the data after all queries are completed
    clear_fetched_data()
    print("Data cleared.")

