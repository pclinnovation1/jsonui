from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import config

my_goals_bp = Blueprint('my_goals_bp', __name__)

# Connect to MongoDB
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
goal_plan_collection = db[config.GOAL_PLAN_COLLECTION_NAME]
my_goals_collection = db[config.My_GOALS_COLLECTION_NAME]

@my_goals_bp.route('/', methods=['POST'])
def fetch_goals():
    data = request.json
    goal_plan_name = data.get('goal_plan_name')
    print("goal_plan_name : ", goal_plan_name)

    if not goal_plan_name:
        return jsonify({'error': 'Goal Plan Name is required'}), 400

    # Fetching the goal plan document based on the goal plan name
    goal_plan = goal_plan_collection.find_one({"details.goal_plan_name": goal_plan_name})
    
    if not goal_plan:
        return jsonify({'error': 'Goal Plan not found'}), 404

    # Fetching include and exclude lists
    include_list = set(goal_plan.get('included_workers', []))
    exclude_list = set(goal_plan.get('excluded_workers', []))

    print("Include list:", include_list)
    print("Exclude list:", exclude_list)

    # Combine include lists with eligibility profiles to get final eligible employees
    eligible_employees = set()
    for profile in goal_plan.get('eligibility_profiles', []):
        eligible_employees.update(profile.get('employees_name', []))
    
    print("Eligible employees from profiles:", eligible_employees)

    # Add include list employees (ensuring include list employees are respected)
    eligible_employees.update(include_list)
    print("Eligible employees after including include_list:", eligible_employees)

    # Check if exclude list is correctly being matched
    for exclude in exclude_list:
        if exclude in eligible_employees:
            print(f"Excluding {exclude}")
        else:
            print(f"Cannot exclude {exclude} because it is not in the eligible list")

    # Remove exclude list employees
    eligible_employees.difference_update(exclude_list)
    print("Eligible employees after excluding exclude_list:", eligible_employees)

    # Retrieve the goal names
    goals = [goal.get('goal_name') for goal in goal_plan.get('goals', [])]
    print("Goals:", goals)

    # Creating my_goals collection entries
    my_goals_entries = []
    for employees_name in eligible_employees:
        for goal_name in goals:
            my_goals_entry = {
                "name": employees_name,
                "goal_plan_assigned": goal_plan_name,
                "goal_name": goal_name,  # Add goal name to the entry
                "progress": "Not started",  # Default value
                "measurement": "None",  # Default value
                "comments": [],
                "feedback": []
            }
            my_goals_entries.append(my_goals_entry)

    # Insert into my_goals collection
    if my_goals_entries:
        result = my_goals_collection.insert_many(my_goals_entries)
        inserted_ids = result.inserted_ids
        # Retrieve the newly inserted documents to include in the response
        my_goals_entries = list(my_goals_collection.find({"_id": {"$in": inserted_ids}}))

    # Convert ObjectIds to strings
    for entry in my_goals_entries:
        entry['_id'] = str(entry['_id'])

    return jsonify({'message': 'Goals successfully assigned', 'my_goals': my_goals_entries}), 200

if __name__ == '__main__':
    my_goals_bp.run(debug=True)
