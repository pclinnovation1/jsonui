from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import config

mass_assign_goals_bp = Blueprint('mass_assign_goals_bp', __name__)

# Connect to MongoDB
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
my_goals_collection = db[config.MY_GOALS_COLLECTION_NAME]
employee_collection = db[config.EMPLOYEE_COLLECTION]

@mass_assign_goals_bp.route('/', methods=['POST'])
def assign_goal_to_all_employees():
    data = request.json
    updated_by = data.get('updated_by', 'Unknown')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print("Received data to add goal:", data)
    
    # Prepare the goal data template
    goal_template = {
        "goal_plan_assigned": data.get("goal_plan_assigned", "N/A"),
        "goal_name": data.get("goal_name"),
        "progress": data.get("progress", "Not started"),
        "measurement": data.get("measurement", "None"),
        "comments": data.get("comments", []),
        "feedback": data.get("feedback", []),
        "updated_by": updated_by,
        "created_at": current_time
    }
    
    print("Prepared goal data template:", goal_template)

    # Fetch all employees
    employees = list(employee_collection.find())
    if not employees:
        return jsonify({'error': 'No employees found'}), 404
    
    print(f"Found {len(employees)} employees")

    # Create goal entries for all employees
    my_goals_entries = []
    for employee in employees:
        goal_data = goal_template.copy()
        goal_data["name"] = employee.get("person_name")
        
        print(f"Prepared goal data for employee {employee.get('person_name')}", goal_data)
        my_goals_entries.append(goal_data)
    
    # Insert the goals into the my_goals collection
    if my_goals_entries:
        print("Inserting entries into my_goals collection")
        result = my_goals_collection.insert_many(my_goals_entries)
        inserted_ids = result.inserted_ids
        print("Inserted IDs:", inserted_ids)
        # Retrieve the newly inserted documents to include in the response
        my_goals_entries = list(my_goals_collection.find({"_id": {"$in": inserted_ids}}))

    # Convert ObjectIds to strings
    for entry in my_goals_entries:
        entry['_id'] = str(entry['_id'])
        print("Converted entry:", entry)

    print("Final my_goals_entries:", my_goals_entries)
    return jsonify({'message': f'Goals successfully assigned to {len(my_goals_entries)} employees', 'my_goals': my_goals_entries}), 201