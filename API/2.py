import requests

# Create dictionaries for ID-to-Name mapping
def create_id_name_mapping(api_url, auth):
    """
    Fetch data from the given route and create a dictionary mapping ID to Name.
    """
    mapping = {}
    try:
        response = requests.get(api_url, auth=auth)
        response.raise_for_status()
        items = response.json().get("items", [])
        mapping = {item["Id"]: item["Name"] for item in items if "Id" in item and "Name" in item}
    except requests.RequestException as e:
        print(f"Error fetching data from {api_url}: {e}")
    return mapping

# Update assignment data with names
def update_assignment_with_names(assignment, mappings):
    """
    Replace IDs in assignment data with corresponding names using the mappings.
    """
    assignment["JobName"] = mappings["jobs"].get(assignment.get("JobId"), "Unknown")
    assignment["PositionName"] = mappings["positions"].get(assignment.get("PositionId"), "Unknown")
    assignment["GradeName"] = mappings["grades"].get(assignment.get("GradeId"), "Unknown")
    assignment["LocationName"] = mappings["locations"].get(assignment.get("LocationId"), "Unknown")
    return assignment

# Main function to process assignment data
def process_assignment_data():
    """
    Process assignments and enrich them with names.
    """
    api_config = CONFIG["api"]
    auth = (api_config['username'], api_config['password'])

    # Define the routes
    jobs_lov_url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/jobsLov"
    positions_lov_url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/positionsLov"
    grades_lov_url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/gradesLov"
    locations_lov_url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/locationsLov"

    # Create mappings
    mappings = {
        "jobs": create_id_name_mapping(jobs_lov_url, auth),
        "positions": create_id_name_mapping(positions_lov_url, auth),
        "grades": create_id_name_mapping(grades_lov_url, auth),
        "locations": create_id_name_mapping(locations_lov_url, auth)
    }

    print("ID-to-Name Mappings Created.")

    # Example assignment data (replace this with your actual assignment data)
    assignment_data = {
        "JobId": 300000004359322,
        "PositionId": 300000004381836,
        "GradeId": 300000017649342,
        "LocationId": 300000002600037,
        "AssignmentNumber": "E000107898"
    }

    # Update assignment data with names
    updated_assignment = update_assignment_with_names(assignment_data, mappings)
    print("Updated Assignment Data:", updated_assignment)

# Run the process
process_assignment_data()
