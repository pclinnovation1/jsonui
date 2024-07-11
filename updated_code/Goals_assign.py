
from pymongo import MongoClient
from datetime import datetime
from eligibility_criteria import check_eligibility  # Import the eligibility check function

# MongoDB client setup
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')  # Adjust the connection string as necessary
db = client['PCL_Interns']  # Database name
goal_plan_collection = db['GOL_GoalPlan']
eligibility_profiles_collection = db['EligibilityProfiles']
employee_details_collection = db['S_EmployeeDetails_UK']
goal_assign_employee_collection = db['Goal_Assign_Employee']
process_details_collection = db['Results_Collection']

# Function to assign goals to employees
def assign_goal(params, process_details_id,db):
    print("into assign goal")
    goal_name = params.get('goal_name')
    eligibility_profile_name = params.get('eligibility_profile_name')

    if not goal_name or not eligibility_profile_name:
        process_details_collection.update_one(
            {'_id': process_details_id},
            {'$set': {'Status': 'Goal_Name and Eligibility_Profile_Name are required'}}
        )
        return "Goal_Name and Eligibility_Profile_Name are required"

    # Retrieve goal details
    goal_details = goal_plan_collection.find_one({"Primary Plan.Goal Plan Name": goal_name})
    if not goal_details:
        process_details_collection.update_one(
            {'_id': process_details_id},
            {'$set': {'Status': 'Goal not found'}}
        )
        return "Goal not found"

    # Retrieve eligibility profile details
    eligibility_profile = eligibility_profiles_collection.find_one({"Create Participant Profile.Eligibility Profile Definition.Name": eligibility_profile_name})
    if not eligibility_profile:
        process_details_collection.update_one(
            {'_id': process_details_id},
            {'$set': {'Status': 'Eligibility profile not found'}}
        )
        return "Eligibility profile not found"

    # Retrieve employees matching the eligibility criteria
    eligibility_criteria = eligibility_profile['Create Participant Profile']['Eligibility Criteria']
    matching_persons = check_eligibility(eligibility_criteria)
    print(f"Matching persons: {matching_persons}")

    if not matching_persons:
        process_details_collection.update_one(
            {'_id': process_details_id},
            {'$set': {'Status': 'No eligible employees found'}}
        )
        return "No eligible employees found"

    # Extract the End Date from the goal details for use as the Due Date
    due_date = goal_details.get('Other Plan', {}).get('Add/View/Edit', {}).get('Details', {}).get('End Date', None)

    # Assign goal to each employee and store in Goal_Assign_Employee collection
    for person_number in matching_persons:
        employee = employee_details_collection.find_one({"Person_Number": person_number})
        person_name = f"{employee['First_Name']} {employee['Last_Name']}"
        goal_assignment = {
            "Person_Number": person_number,
            "Person_Name": person_name,
            "Goal_Name": goal_details['Primary Plan']['Goal Plan Name'],
            "Goal_Description": goal_details['Primary Plan']['Description'],
            "Review_Period": goal_details['Primary Plan']['Review Period'],
            "Assigned_Date": datetime.now().strftime('%Y-%m-%d'),
            "Due_Date": due_date,
            "Timestamp": datetime.now()
        }
        goal_assign_employee_collection.insert_one(goal_assignment)

    process_details_collection.update_one(
        {'_id': process_details_id},
        {'$set': {'Status': 'Completed'}}
    )

    return f"Assigned {goal_name} to eligible employees"
