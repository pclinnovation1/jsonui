from flask import Blueprint, request, jsonify, Flask
from journey_management import (
    add_user_to_journey, 
    create_journey,
    update_journey,
    delete_journey,
    remove_task_eligibility_profile,
    complete_task,
    submit_feedback,
    add_task_eligibility_profile,
    create_task,
    update_task,
    delete_task,
    add_eligibility_profile,
    remove_eligibility_profile,
    update_time_status,
    assign_onboarding_journeys_for_today,
    update_status_for_completed_tasks,
    assign_offboarding_journeys_for_today,
    unassign_journey_from_user,
    remove_employee_and_cleanup_journeys,
    add_task_to_journeyf,
    send_overdue_task_notifications,
    remove_task_from_journey
)
app = Flask(__name__)
journey_bp = Blueprint('journey_bp', __name__)

#HR or Manager
@app.route('/create_journey', methods=['POST'])
def create_new_journey():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    result, status_code= create_journey(data)
    return jsonify(result), status_code

#HR or Manager
@app.route('/create_task', methods=['POST'])
def create_task_route():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    result, status_code = create_task(data)
    return jsonify(result), status_code

#HR or manager
@app.route('/add_user_to_journey', methods=['POST'])
def add_user():
    data = request.json
    journey_title = data.get("journey_name")
    user = data.get("users")
    if not journey_title or not user:
        return jsonify({"error": "Missing journey_title or user in request body"}), 400
    result, status_code = add_user_to_journey(journey_title, user, data)
    return jsonify(result), status_code

#HR or manager
@app.route('/add_task_to_journey', methods=['POST'])
def add_task_to_journey():
    try:
        # Extract data from the request
        journey_title = request.json.get('journey_name')
        task_name = request.json.get('task_name')
        eligibility_profiles = request.json.get('eligibility_profiles',[])

        if not journey_title or not task_name:
            return jsonify({"error": "All of these 'journey_title' and 'task_name' are required."}), 400
        
        updated_by= request.json.get('updated_by')
        if not updated_by:
          updated_by= 'Admin'
        # Call the function to add the task to the existing users and teams
        result = add_task_to_journeyf(journey_title, task_name,eligibility_profiles,updated_by)

        # Return the result
 
        return jsonify({"result": result}), 200
 
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#scheduler
@app.route('/assign_onboarding_journeys_for_today', methods=['POST'])
def assign_onboarding_journeys_for_today_route():
    result, status_code = assign_onboarding_journeys_for_today()
    return jsonify(result), status_code

#scheduler
@app.route('/assign_offboarding_journeys_for_today', methods=['POST'])
def assign_offboarding_journeys_for_today_route():
    result, status_code = assign_offboarding_journeys_for_today()
    return jsonify(result), status_code

#HR or Manager
@app.route('/unassign_journey', methods=['POST'])
def unassign_journey():
    data = request.json

    # Validate request data
    if not data or 'journey_name' not in data or 'person_name' not in data:
        return jsonify({'error': 'Please provide journey_name and person_name'}), 400

    journey_title = data['journey_name']
    person_name = data['person_name']
    updated_by=data.get('updated_by','Admin')
    # Call the function to unassign the journey
    response, status_code = unassign_journey_from_user(journey_title, person_name, updated_by)
    
    return jsonify(response), status_code

#HR or Manager
@app.route('/remove_employee', methods=['POST'])
def remove_employee():
    data = request.get_json()
    person_name = data.get('person_name')
    updated_by=data.get('updated_by','Admin')
    if not person_name:
        return jsonify({"error": "person_name is required"}), 400

    response, status_code = remove_employee_and_cleanup_journeys(person_name,updated_by)
    return jsonify(response), status_code

#employee manager or hr anyone can use
@app.route('/complete_task', methods=['POST'])
def complete_task_route():
    data = request.json
    person_name = data.get("person_name")
    journey_title = data.get("journey_name")
    task_name = data.get("task_name")
    action_name = data.get("action_name")

    if not person_name or not journey_title or not task_name or not action_name:
        return jsonify({"error": "Missing person_name, journey_title,action_name, or task_name in request body"}), 400

    result, status_code = complete_task(person_name, journey_title, task_name,action_name)
    return jsonify(result), status_code

#scheduler
@app.route('/update_status_for_completed_tasks', methods=['POST'])
def run_update_status_for_completed_tasks():
    result, status_code = update_status_for_completed_tasks()
    return jsonify(result), status_code

#HR or Manager
@app.route('/update_task', methods=['POST'])
def update_task_route():
    data = request.json
    task_name = data.get("task_name")
    update_data = data.get("update_data")

    if not task_name or not update_data:
        return jsonify({"error": "Missing task_name or update_data in request body"}), 400

    result, status_code = update_task(task_name, update_data)
    return jsonify(result), status_code

#HR or Manager
@app.route('/update_journey', methods=['POST'])
def update_existing_journey():
    data = request.json
    if not data or "journey_name" not in data:
        return jsonify({"error": "Missing journey_name"}), 400
    
    if 'category' in data or 'description' in data:
        journey_title = data["journey_name"]
        category=data.get('category')
        description=data.get('description')
        updated_by=data.get('updated_by','Admin')
    else : return jsonify({"error": "Missing both category and description in request body"}), 400
    result, status_code = update_journey(journey_title, category, description, updated_by)
    return jsonify(result), status_code

#HR or Manager
@app.route('/delete_journey', methods=['POST'])
def delete_existing_journey():
    data = request.json
    if not data or "journey_name" not in data:
        return jsonify({"error": "Missing journey_title in request body"}), 400

    journey_title = data["journey_name"]

    result, status_code = delete_journey(journey_title)
    return jsonify(result), status_code

#HR or Manager
@app.route('/delete_task', methods=['POST'])
def delete_task_route():
    data = request.json
    task_name = data.get("task_name")
    updated_by=data.get('updated_by','Admin')
    if not task_name:
        return jsonify({"error": "Missing task_name in request body"}), 400

    result, status_code = delete_task(task_name, updated_by)
    return jsonify(result), status_code

#HR or Manager
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback_route():
    data = request.json
    person_name = data.get("person_name")
    journey_title = data.get("journey_name")
    task_name = data.get("task_name")
    feedback = data.get("feedback")
    action_name = data.get("action_name")
    
    if not person_name or not journey_title or not task_name or not feedback or not action_name:
        return jsonify({"error": "Missing person_name, journey_title, task_name, or feedback in request body"}), 400

    result, status_code = submit_feedback(person_name, journey_title,task_name, action_name,feedback)
    return jsonify(result), status_code

#HR or Manager
@app.route('/remove_task_from_journey', methods=['POST'])
def remove_task_from_journey_route():
    data = request.json
    journey_title = data.get('journey_name')
    task_name_to_remove = data.get('task_name')

    # Ensure both journey title and task name are provided
    if not journey_title or not task_name_to_remove:
        return jsonify({'error': 'Missing journey_title or task_name'}), 400
    updated_by=data.get('updated_by','Admin')
    # Call the function to remove the task from the journey
    result, status_code = remove_task_from_journey(journey_title, task_name_to_remove, updated_by)

    return jsonify(result), status_code

#scheduler
@app.route('/update_time_status', methods=['POST'])
def update_time_status_route():
    result, status_code = update_time_status()
    return jsonify(result), status_code

#scheduler
@app.route('/send_overdue_task_notifications', methods=['POST'])
def send_overdue_task_notifications2():
    result, status_code = send_overdue_task_notifications()
    return jsonify(result), status_code

#HR or Manager
@app.route('/add_eligibility_profile_to_j',methods=['POST'])
def add_eligibility_profile_to_j():
    data = request.json
    journey_title = data.get('journey_name')
    eligibility_profile_to_add = data.get('eligibility_profile')

    if not data or not journey_title or not eligibility_profile_to_add:
        return jsonify({"error": "Missing required fields"}), 400
    
    updated_by=data.get('updated_by','Admin')

    result, status_code = add_eligibility_profile(journey_title, eligibility_profile_to_add, updated_by)
    return jsonify(result), status_code

#HR or Manager
@app.route('/remove_eligibility_profile_j',methods=['POST'])
def remove_eligibility_profile_j():
    data = request.json
    journey_title = data.get('journey_name')
    eligibility_profile_to_remove = data.get('eligibility_profile')

    if not data or not journey_title or not eligibility_profile_to_remove:
        return jsonify({"error": "Missing required fields"}), 400
    
    updated_by=data.get('updated_by','Admin')

    result, status_code = remove_eligibility_profile(journey_title, eligibility_profile_to_remove, updated_by)
    return jsonify(result), status_code

#HR or Manager
@app.route('/add_eligibility_profile_to_t',methods=['POST'])
def add_eligibility_profile_to_t():
    data = request.json
    journey_title = data.get('journey_name')
    task_name=data.get('task_name')
    eligibility_profile_to_add = data.get('eligibility_profile')

    if not data or not journey_title or not eligibility_profile_to_add or not task_name:
        return jsonify({"error": "Missing required fields"}), 400
    
    updated_by=data.get('updated_by','Admin')

    result, status_code = add_task_eligibility_profile(journey_title, task_name, eligibility_profile_to_add, updated_by)
    return jsonify(result), status_code

#HR or Manager
@app.route('/remove_eligibility_profile_t',methods=['POST'])
def remove_eligibility_profile_t():
    data = request.json
    journey_title = data.get('journey_name')
    task_name=data.get('task_name')
    eligibility_profile_to_remove = data.get('eligibility_profile')

    if not data or not journey_title or not eligibility_profile_to_remove or not task_name:
        return jsonify({"error": "Missing required fields"}), 400
    
    updated_by=data.get('updated_by','Admin')

    result, status_code = remove_task_eligibility_profile(journey_title, task_name, eligibility_profile_to_remove, updated_by)
    return jsonify(result), status_code

if __name__ == '__main__':
    app.run(debug=True, port=5003)

# -------------------------------------------------------------------------------
