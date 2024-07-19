from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["Goals_performance"]

def update_assignees_count(plan_name):
    goal_plan = db.goal_plans.find_one({"Plan Name": plan_name})
    if goal_plan:
        total_assignees = len(goal_plan.get("Included Employees", [])) - len(goal_plan.get("Excluded Employees", []))
        db.goal_plans.update_one(
            {"Plan Name": plan_name},
            {"$set": {"Assignees": total_assignees}}
        )

# Routes for creating, viewing, updating and managing goal plans
@app.route('/goal_plans/create', methods=['POST'])
def create_goal_plan():
    data = request.json
    db.goal_plans.insert_one(data)
    update_assignees_count(data["Plan Name"])
    return jsonify({"message": "Goal plan created successfully"}), 201

@app.route('/goal_plans', methods=['POST'])
def get_goal_plans():
    data = request.json
    plan_name = data.get('Plan Name')
    review_period = data.get('Review Period')
    status = data.get('Status')
    weight_enabled = data.get('Weight Enabled')
    start_date = data.get('Start Date')
    end_date = data.get('End Date')

    query = {}
    if plan_name:
        query['Plan Name'] = plan_name
    if review_period:
        query['Review Period'] = review_period
    if status:
        query['Status'] = status
    if weight_enabled:
        query['Weight Enabled'] = weight_enabled
    if start_date:
        query['Start Date'] = {"$gte": start_date}
    if end_date:
        query['End Date'] = {"$lte": end_date}

    goal_plans = list(db.goal_plans.find(query, {'_id': 0}))
    return jsonify(goal_plans)

@app.route('/goal_plans/details', methods=['POST'])
def get_goal_plan_details():
    data = request.json
    plan_name = data.get('Plan Name')

    query = {}
    if plan_name:
        query['Plan Name'] = plan_name

    goal_plan = db.goal_plans.find_one(query, {'_id': 0})
    return jsonify(goal_plan)

@app.route('/goal_plans/update', methods=['POST'])
def update_goal_plan():
    data = request.json
    plan_name = data['Plan Name']
    updates = data['Updates']

    db.goal_plans.update_one(
        {"Plan Name": plan_name},
        {"$set": updates}
    )
    update_assignees_count(plan_name)
    return jsonify({"message": "Goal plan updated successfully"})

@app.route('/goal_plans/add_goals', methods=['POST'])
def add_goals_to_plan():
    data = request.json
    plan_name = data['Plan Name']
    new_goals = data['Goals']

    db.goal_plans.update_one(
        {"Plan Name": plan_name},
        {"$push": {"Goals": {"$each": new_goals}}}
    )
    return jsonify({"message": "Goals added to plan successfully"})

@app.route('/goal_plans/remove_goals', methods=['POST'])
def remove_goals_from_plan():
    data = request.json
    plan_name = data['Plan Name']
    goal_names = data['Goal Names']

    db.goal_plans.update_one(
        {"Plan Name": plan_name},
        {"$pull": {"Goals": {"Goal Name": {"$in": goal_names}}}}
    )
    return jsonify({"message": "Goals removed from plan successfully"})

@app.route('/goal_plans/add_eligibility_profiles', methods=['POST'])
def add_eligibility_profiles_to_plan():
    data = request.json
    plan_name = data['Plan Name']
    profile_names = data['Profile Names']

    # Check if all the eligibility profiles exist
    profiles = list(db.eligibility_profiles.find({"Profile Name": {"$in": profile_names}}, {'_id': 0}))
    if len(profiles) != len(profile_names):
        return jsonify({"message": "One or more eligibility profiles not found"}), 404

    db.goal_plans.update_one(
        {"Plan Name": plan_name},
        {"$push": {"Eligibility Profiles": {"$each": profiles}}}
    )
    return jsonify({"message": "Eligibility profiles added to plan successfully"})

@app.route('/goal_plans/remove_eligibility_profiles', methods=['POST'])
def remove_eligibility_profiles_from_plan():
    data = request.json
    plan_name = data['Plan Name']
    profile_names = data['Profile Names']

    db.goal_plans.update_one(
        {"Plan Name": plan_name},
        {"$pull": {"Eligibility Profiles": {"Profile Name": {"$in": profile_names}}}}
    )
    return jsonify({"message": "Eligibility profiles removed from plan successfully"})

@app.route('/goal_plans/add_included_employees', methods=['POST'])
def add_included_employees_to_plan():
    data = request.json
    plan_name = data['Plan Name']
    new_employees = data['Employees']

    db.goal_plans.update_one(
        {"Plan Name": plan_name},
        {"$push": {"Included Employees": {"$each": new_employees}}}
    )
    update_assignees_count(plan_name)
    return jsonify({"message": "Included employees added to plan successfully"})

@app.route('/goal_plans/remove_included_employees', methods=['POST'])
def remove_included_employees_from_plan():
    data = request.json
    plan_name = data['Plan Name']
    employee_names = data['Employee Names']

    db.goal_plans.update_one(
        {"Plan Name": plan_name},
        {"$pull": {"Included Employees": {"Name": {"$in": employee_names}}}}
    )
    update_assignees_count(plan_name)
    return jsonify({"message": "Included employees removed from plan successfully"})

@app.route('/goal_plans/add_excluded_employees', methods=['POST'])
def add_excluded_employees_to_plan():
    data = request.json
    plan_name = data['Plan Name']
    new_employees = data['Employees']

    db.goal_plans.update_one(
        {"Plan Name": plan_name},
        {"$push": {"Excluded Employees": {"$each": new_employees}}}
    )
    update_assignees_count(plan_name)
    return jsonify({"message": "Excluded employees added to plan successfully"})

@app.route('/goal_plans/remove_excluded_employees', methods=['POST'])
def remove_excluded_employees_from_plan():
    data = request.json
    plan_name = data['Plan Name']
    employee_names = data['Employee Names']

    db.goal_plans.update_one(
        {"Plan Name": plan_name},
        {"$pull": {"Excluded Employees": {"Name": {"$in": employee_names}}}}
    )
    update_assignees_count(plan_name)
    return jsonify({"message": "Excluded employees removed from plan successfully"})

if __name__ == '__main__':
    app.run(debug=True)
