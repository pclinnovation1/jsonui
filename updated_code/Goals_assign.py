# from pymongo import MongoClient
# from datetime import datetime
# from bson import ObjectId

# from eligibility_criteria import check_eligibility  # Import the eligibility check function

# # MongoDB client setup
# client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')  # Adjust the connection string as necessary
# db = client['PCL_Interns']  # Database name
# goal_plan_collection = db['GOL_GoalPlan']
# eligibility_profiles_collection = db['EligibilityProfiles']
# employee_details_collection = db['S_EmployeeDetails_UK']
# goal_assign_employee_collection = db['Goal_Assign_Employee']
# process_details_collection = db['Results_Collection']

# # Function to assign goals to employees
# def assign_goal(params, process_details_id, db):
#     print("into assign goal")
#     goal_name = params.get('goal_name')
#     eligibility_profile_name = params.get('eligibility_profile_name')

#     if not goal_name or not eligibility_profile_name:
#         status = "Goal_Name and Eligibility_Profile_Name are required"
#         return status
#     # Retrieve goal details
#     goal_details = goal_plan_collection.find_one({"Primary Plan.Goal Plan Name": goal_name})
#     if not goal_details:
#         status =  "Goal not found"
#         return status

#     # Retrieve eligibility profile details
#     eligibility_profile = eligibility_profiles_collection.find_one({"Create Participant Profile.Eligibility Profile Definition.Name": eligibility_profile_name})
#     if not eligibility_profile:
#         status =  "Eligibility profile not found"
#         return status

#     # Retrieve employees matching the eligibility criteria
#     eligibility_criteria = eligibility_profile['Create Participant Profile']['Eligibility Criteria']
#     matching_persons = check_eligibility(eligibility_criteria)
#     print(f"Matching persons: {matching_persons}")

#     if not matching_persons:
#         return "No eligible employees found"
    
#     status = "Completed"

#     # Extract the End Date from the goal details for use as the Due Date
#     due_date = goal_details.get('Other Plan', {}).get('Add/View/Edit', {}).get('Details', {}).get('End Date', None)

#     # Assign goal to each employee and store in Goal_Assign_Employee collection
#     for person_number in matching_persons:
#         employee = employee_details_collection.find_one({"Person_Number": person_number})
#         person_name = f"{employee['First_Name']} {employee['Last_Name']}"
#         goal_assignment = {
#             "Person_Number": person_number,
#             "Person_Name": person_name,
#             "Goal_Name": goal_details['Primary Plan']['Goal Plan Name'],
#             "Goal_Description": goal_details['Primary Plan']['Description'],
#             "Review_Period": goal_details['Primary Plan']['Review Period'],
#             "Assigned_Date": datetime.now().strftime('%Y-%m-%d'),
#             "Due_Date": due_date,
#             "Timestamp": datetime.now()
#         }
#         goal_assign_employee_collection.insert_one(goal_assignment)

#     return status


# if __name__ == "__main__":

#     # Example parameters for assigning a goal
#     params = {
#         'goal_name': 'Annual Performance Plan',
#         'eligibility_profile_name': 'Standard Eligibility'
#     }

#     # Example process details ID (assuming it is an ObjectId from MongoDB)
#     process_details_id = ObjectId('60c72b2f9b7e4f3a4f9e76f4')  # Replace with a valid ObjectId

#     # Call the assign_goal function with the example parameters
#     result = assign_goal(params, process_details_id, db)

#     # Print the result
#     print(result)



# # Execute the example call














from pymongo import MongoClient
from datetime import datetime
from eligibility_criteria import check_eligibility  # Import the eligibility check function
import logging
from bson import ObjectId

# MongoDB client setup
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')  # Adjust the connection string as necessary
db = client['PCL_Interns']  # Database name
goal_plan_collection = db['GOL_GoalPlan']
eligibility_profiles_collection = db['EligibilityProfiles']
employee_details_collection = db['S_EmployeeDetails_UK']
goal_assign_employee_collection = db['Goal_Assign_Employee']
process_details_collection = db['Results_Collection']

# Initialize logger
logging.basicConfig(level=logging.DEBUG)

# Function to assign goals to employees
def assign_goal(params, process_details_id, db):
    print("into goal assign")
    logging.info("Starting goal assignment process")
    goal_name = params.get('goal_name')
    eligibility_profile_name = params.get('eligibility_profile_name')

    if not goal_name or not eligibility_profile_name:
        status = "Goal_Name and Eligibility_Profile_Name are required"
        process_details_collection.update_one(
            {'_id': ObjectId(process_details_id)},
            {'$set': {'Status': status}}
        )
        logging.error(status)
        return status

    try:
        # Retrieve goal details
        goal_details = goal_plan_collection.find_one({"Primary Plan.Goal Plan Name": goal_name})
        if not goal_details:
            status = "Goal not found"
            process_details_collection.update_one(
                {'_id': ObjectId(process_details_id)},
                {'$set': {'Status': status}}
            )
            logging.error(status)
            return status

        # Retrieve eligibility profile details
        eligibility_profile = eligibility_profiles_collection.find_one({"Create Participant Profile.Eligibility Profile Definition.Name": eligibility_profile_name})
        if not eligibility_profile:
            status = "Eligibility profile not found"
            process_details_collection.update_one(
                {'_id': ObjectId(process_details_id)},
                {'$set': {'Status': status}}
            )
            logging.error(status)
            return status

        # Retrieve employees matching the eligibility criteria
        eligibility_criteria = eligibility_profile['Create Participant Profile']['Eligibility Criteria']
        matching_persons = check_eligibility(eligibility_criteria)
        logging.info(f"Matching persons: {matching_persons}")

        if not matching_persons:
            status = "No eligible employees found"
            process_details_collection.update_one(
                {'_id': ObjectId(process_details_id)},
                {'$set': {'Status': status}}
            )
            logging.info(status)
            return status

        # Extract the End Date from the goal details for use as the Due Date
        due_date = goal_details.get('Other Plan', {}).get('Add/View/Edit', {}).get('Details', {}).get('End Date', None)
        logging.info(f"Due date for the goal: {due_date}")

        # Assign goal to each employee and store in Goal_Assign_Employee collection
        for person_number in matching_persons:
            employee = employee_details_collection.find_one({"Person_Number": person_number})
            if not employee:
                logging.warning(f"Employee with Person_Number {person_number} not found")
                continue
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
            logging.info(f"Assigned goal to {person_name} ({person_number})")

        status = "Completed"
        process_details_collection.update_one(
            {'_id': ObjectId(process_details_id)},
            {'$set': {'Status': status}}
        )
        logging.info(f"Goal assignment process status: {status}")
        return f"Assigned {goal_name} to eligible employees"

    except Exception as e:
        status = "Failed"
        process_details_collection.update_one(
            {'_id': ObjectId(process_details_id)},
            {'$set': {'Status': status}}
        )
        logging.error(f"Error in goal assignment: {e}")
        return status

if __name__ == "__main__":
    # Example parameters for assigning a goal
    params = {
        'goal_name': 'Annual Performance Plan',
        'eligibility_profile_name': 'Standard Eligibility'
    }

    # Example process details ID (assuming it is an ObjectId from MongoDB)
    process_details_id = ObjectId()  # This will create a new ObjectId for testing

    # Insert a dummy process details entry for testing
    process_details_collection.insert_one({
        '_id': process_details_id,
        'Status': 'Pending',
        'Created_At': datetime.now()
    })

    # Call the assign_goal function with the example parameters
    result = assign_goal(params, process_details_id, db)

    # Print the result
    print(result)
    # Verify the updated status in the process details collection
    updated_process_details = process_details_collection.find_one({'_id': process_details_id})
    print(f"Updated process details: {updated_process_details}")
