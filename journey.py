from flask import Blueprint, request, jsonify, Flask
from journey_management import (
    add_user_to_journey, 
    view_journeys_of_user, 
    view_all_journeys,
    create_journey,
    update_journey,
    delete_journey,
    view_my_journeys,
    track_journey_progress,
    complete_task,
    submit_feedback,
    view_team_journeys,
    track_team_member_progress,
    update_task_status_for_team_member,
    provide_feedback_on_team_member_task,
    monitor_overall_journey_progress,
    generate_reports,
    add_user_to_team_in_journey,
    create_task,
    update_task,
    view_task,
    delete_task,
    show_my_tasks,
    show_team_journey_tasks_and_report,
    show_journey_activities,
    update_time_status,
    view_journey_by_name,
    track_one_journey_progress,
    add_team,
    add_employee,
    assign_onboarding_journeys_for_today,
    update_status_for_completed_tasks,
    assign_offboarding_journeys_for_today,
    unassign_journey_from_user,
    add_user_to_journey2,
    remove_employee_and_cleanup_journeys,
    unassign_journey_from_user_for_team,
    add_task_to_existing_users_and_teams,
    send_overdue_task_notifications,
    remove_task_from_journey
)

app = Flask(__name__)
journey_bp = Blueprint('journey_bp', __name__)

@app.route('/remove_employee', methods=['POST'])
def remove_employee():
    data = request.get_json()
    person_name = data.get('person_name')

    if not person_name:
        return jsonify({"error": "person_name is required"}), 400

    response, status_code = remove_employee_and_cleanup_journeys(person_name)
    return jsonify(response), status_code

@app.route('/unassign_journey', methods=['POST'])
def unassign_journey():
    data = request.json

    # Validate request data
    if not data or 'journey_title' not in data or 'person_name' not in data:
        return jsonify({'error': 'Please provide journey_title and person_name'}), 400

    journey_title = data['journey_title']
    person_name = data['person_name']

    # Call the function to unassign the journey
    response, status_code = unassign_journey_from_user(journey_title, person_name)
    
    return jsonify(response), status_code

@app.route('/unassign_journey_for_team', methods=['POST'])
def unassign_journey_from_team():
    data = request.json

    # Validate request data
    if not data or 'journey_title' not in data or 'person_name' not in data:
        return jsonify({'error': 'Please provide journey_title and person_name'}), 400

    journey_title = data['journey_title']
    person_name = data['person_name']

    # Call the function to unassign the journey
    response, status_code = unassign_journey_from_user_for_team(journey_title, person_name)
    
    return jsonify(response), status_code

@app.route('/add_user_to_journey', methods=['POST'])
def add_user():
    data = request.json
    journey_title = data.get("name")
    user = data.get("users")

    if not journey_title or not user:
        return jsonify({"error": "Missing journey_title or user in request body"}), 400

    result, status_code = add_user_to_journey(journey_title, user)
    return jsonify(result), status_code
#only add task to employee not it's manager and HR
@app.route('/add_user_to_journey2', methods=['POST'])
def add_user2():
    data = request.json
    journey_title = data.get("name")
    user = data.get("users")

    if not journey_title or not user:
        return jsonify({"error": "Missing journey_title or user in request body"}), 400

    result, status_code = add_user_to_journey2(journey_title, user)
    return jsonify(result), status_code

@app.route('/view_journeys_of_user', methods=['POST'])
def view_user_journeys():
    data = request.json
    user_name = data.get("users")

    if not user_name:
        return jsonify({"error": "Missing user_name in request body"}), 400

    result, status_code = view_journeys_of_user(user_name)
    return jsonify(result), status_code

@app.route('/create_journey', methods=['POST'])
def create_new_journey():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    result, status_code = create_journey(data)
    return jsonify(result), status_code

@app.route('/update_journey', methods=['POST'])
def update_existing_journey():
    data = request.json
    if not data or "name" not in data or "update_data" not in data:
        return jsonify({"error": "Missing journey_title or update_data in request body"}), 400

    journey_title = data["name"]
    update_data = data["update_data"]

    result, status_code = update_journey(journey_title, update_data)
    return jsonify(result), status_code

@app.route('/delete_journey', methods=['POST'])
def delete_existing_journey():
    data = request.json
    if not data or "name" not in data:
        return jsonify({"error": "Missing journey_title in request body"}), 400

    journey_title = data["name"]

    result, status_code = delete_journey(journey_title)
    return jsonify(result), status_code

@app.route('/view_my_journeys', methods=['POST'])
def view_my_journeys_route():
    data = request.json
    person_name = data.get("person_name")

    if not person_name:
        return jsonify({"error": "Missing person_name in request body"}), 400

    result, status_code = view_my_journeys(person_name)
    return jsonify(result), status_code

@app.route('/track_journey_progress', methods=['POST'])
def track_journey_progress_route():
    result, status_code = track_journey_progress()
    return jsonify(result), status_code

@app.route('/complete_task', methods=['POST'])
def complete_task_route():
    data = request.json
    person_name = data.get("person_name")
    journey_title = data.get("journey_title")
    task_name = data.get("task_name")
    action_name = data.get("action_name")

    if not person_name or not journey_title or not task_name or not action_name:
        return jsonify({"error": "Missing person_name, journey_title,action_name, or task_name in request body"}), 400

    result, status_code = complete_task(person_name, journey_title, task_name,action_name)
    return jsonify(result), status_code

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback_route():
    data = request.json
    person_name = data.get("person_name")
    journey_title = data.get("journey_title")
    task_name = data.get("task_name")
    feedback = data.get("feedback")
    action_name = data.get("action_name")
    

    if not person_name or not journey_title or not task_name or not feedback or not action_name:
        return jsonify({"error": "Missing person_name, journey_title, task_name, or feedback in request body"}), 400

    result, status_code = submit_feedback(person_name, journey_title,task_name, action_name,feedback)
    return jsonify(result), status_code

@app.route('/view_team_journeys', methods=['POST'])
def view_team_journeys_route():
    data = request.json
    team_name = data.get("team_name")

    if not team_name:
        return jsonify({"error": "Missing team_name in request body"}), 400

    result, status_code = view_team_journeys(team_name)
    return jsonify(result), status_code

@app.route('/track_team_member_progress', methods=['POST'])
def track_team_member_progress_route():
    data = request.json
    team_name = data.get("team_name")
    member_name = data.get("member_name")

    if not team_name or not member_name:
        return jsonify({"error": "Missing team_name or member_name in request body"}), 400

    result, status_code = track_team_member_progress(team_name, member_name)
    return jsonify(result), status_code

@app.route('/update_task_status_for_team_member', methods=['POST'])
def update_task_status_for_team_member_route():
    data = request.json
    team_name = data.get("team_name")
    member_name = data.get("member_name")
    journey_title = data.get("journey_title")
    task_name = data.get("task_name")
    action_name = data.get("action_name")
    

    if not team_name or not member_name or not journey_title or not task_name or not action_name:
        return jsonify({"error": "Missing team_name, member_name, journey_title, task_name, or action_name in request body"}), 400

    result, status_code = update_task_status_for_team_member(team_name, member_name, journey_title, task_name,action_name)
    return jsonify(result), status_code

@app.route('/provide_feedback_on_team_member_task', methods=['POST'])
def provide_feedback_on_team_member_task_route():
    data = request.json
    team_name = data.get("team_name")
    member_name = data.get("member_name")
    journey_title = data.get("journey_title")
    task_name = data.get("task_name")
    feedback = data.get("feedback")
    action_name = data.get("action_name")

    if not team_name or not member_name or not journey_title or not task_name or not feedback or not action_name:
        return jsonify({"error": "Missing team_name, member_name, journey_title, task_name, or feedback or action_name in request body"}), 400

    result, status_code = provide_feedback_on_team_member_task(team_name, member_name, journey_title, task_name, feedback,action_name)
    return jsonify(result), status_code

@app.route('/monitor_overall_journey_progress', methods=['POST'])
def monitor_overall_journey_progress_route():
    result, status_code = monitor_overall_journey_progress()
    return jsonify(result), status_code

@app.route('/generate_reports', methods=['POST'])
def generate_reports_route():
    result, status_code = generate_reports()
    return jsonify(result), status_code

@app.route('/add_user_to_team_in_journey', methods=['POST'])
def add_user_to_team_in_journey_route():
    data = request.json
    journey_title = data.get("journey_title")
    team_name = data.get("team_name")
    member_name = data.get("member_name")

    if not journey_title or not team_name or not member_name:
        return jsonify({"error": "Missing journey_title, team_name, or member_name in request body"}), 400

    result, status_code = add_user_to_team_in_journey(journey_title, team_name, member_name)
    return jsonify(result), status_code

@app.route('/create_task', methods=['POST'])
def create_task_route():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    result, status_code = create_task(data)
    return jsonify(result), status_code

@app.route('/update_task', methods=['POST'])
def update_task_route():
    data = request.json
    task_name = data.get("task_name")
    update_data = data.get("update_data")

    if not task_name or not update_data:
        return jsonify({"error": "Missing task_name or update_data in request body"}), 400

    result, status_code = update_task(task_name, update_data)
    return jsonify(result), status_code


@app.route('/add_task_to_journey', methods=['POST'])
def add_task_to_journey():
    try:
        # Extract data from the request
        journey_title = request.json.get('journey_title')
        task_name = request.json.get('task_name')

        if not journey_title or not task_name:
            return jsonify({"error": "Both 'journey_title' and 'task_name' are required."}), 400

        # Call the function to add the task to the existing users and teams
        result = add_task_to_existing_users_and_teams(journey_title, task_name)

        # Return the result
 
        return jsonify({"message": "Task added successfully", "result": result}), 200
 

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/remove_task_from_journey', methods=['POST'])
def remove_task_from_journey_route():
    data = request.json
    journey_title = data.get('journey_title')
    task_name_to_remove = data.get('task_name')

    # Ensure both journey title and task name are provided
    if not journey_title or not task_name_to_remove:
        return jsonify({'error': 'Missing journey_title or task_name'}), 400

    # Call the function to remove the task from the journey
    result, status_code = remove_task_from_journey(journey_title, task_name_to_remove)

    return jsonify(result), status_code

@app.route('/view_task', methods=['POST'])
def view_task_route():
    data = request.json
    task_name = data.get("task_name")

    if not task_name:
        return jsonify({"error": "Missing task_name in request body"}), 400

    result, status_code = view_task(task_name)
    return jsonify(result), status_code

@app.route('/delete_task', methods=['POST'])
def delete_task_route():
    data = request.json
    task_name = data.get("task_name")

    if not task_name:
        return jsonify({"error": "Missing task_name in request body"}), 400

    result, status_code = delete_task(task_name)
    return jsonify(result), status_code

@app.route('/show_my_tasks', methods=['POST'])
def show_my_tasks_route():
    data = request.json
    person_name = data.get("person_name")

    if not person_name:
        return jsonify({"error": "Missing person_name in request body"}), 400

    result, status_code = show_my_tasks(person_name)
    return jsonify(result), status_code

@app.route('/show_team_journey_tasks_and_report', methods=['POST'])
def show_team_journey_tasks_and_report_route():
    data = request.json
    team_name = data.get("team_name")
    member_name = data.get("member_name")

    if not team_name or not member_name:
        return jsonify({"error": "Missing team_name or member_name in request body"}), 400

    result, status_code = show_team_journey_tasks_and_report(team_name, member_name)
    return jsonify(result), status_code

@app.route('/show_journey_activities', methods=['POST'])
def show_journey_activities_route():
 

    result, status_code = show_journey_activities()
    return jsonify(result), status_code

@app.route('/update_time_status', methods=['POST'])
def update_time_status_route():
    result, status_code = update_time_status()
    return jsonify(result), status_code


# Flask route
@app.route('/update_status_for_completed_tasks', methods=['POST'])
def run_update_status_for_completed_tasks():
    result, status_code = update_status_for_completed_tasks()
    return jsonify(result), status_code

@app.route('/send_overdue_task_notifications', methods=['POST'])
def send_overdue_task_notifications2():
    result, status_code = send_overdue_task_notifications()
    return jsonify(result), status_code



@app.route('/view_journey_by_name', methods=['POST'])
def view_journey_by_name_route():
    data = request.json
    journey_name = data.get("journey_name")

    if not journey_name:
        return jsonify({"error": "Missing journey_name in request body"}), 400

    result, status_code = view_journey_by_name(journey_name)
    return jsonify(result), status_code

@app.route('/track_one_journey_progress', methods=['POST'])
def track_one_journey_progress_route():
    data = request.json
    journey_name = data.get("journey_name")

    if not journey_name:
        return jsonify({"error": "Missing journey_name in request body"}), 400

    result, status_code = track_one_journey_progress(journey_name)
    return jsonify(result), status_code

@app.route('/add_team', methods=['POST'])
def add_team_route():
    data = request.json
    journey_name = data.get("journey_name")
    team_data = {
        'team_name': data.get("team_name"),
        'journey_start_date': data.get("journey_start_date"),
        'journey_due_date': data.get("journey_due_date"),
        'status': data.get("status"),
        'teammembers': data.get("teammembers")
    }

    if not journey_name or not team_data:
        return jsonify({"error": "Missing journey_name or team_data in request body"}), 400

    result, status_code = add_team(journey_name, team_data)
    return jsonify(result), status_code

@app.route('/add_employee', methods=['POST'])
def add_employee_route():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    result, status_code = add_employee(data)
    return jsonify(result), status_code

@app.route('/assign_onboarding_journeys_for_today', methods=['POST'])
def assign_onboarding_journeys_for_today_route():
    result, status_code = assign_onboarding_journeys_for_today()
    return jsonify(result), status_code

@app.route('/assign_offboarding_journeys_for_today', methods=['POST'])
def assign_offboarding_journeys_for_today_route():
    result, status_code = assign_offboarding_journeys_for_today()
    return jsonify(result), status_code

@app.route('/view_all_journeys', methods=['POST'])
def view_all_journeys_route():
    result, status_code = view_all_journeys()
    return jsonify(result), status_code



if __name__ == '__main__':
    app.run(debug=True, port=5003)
