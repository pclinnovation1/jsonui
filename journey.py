# journey_routes.py
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
    generate_reports
)

app = Flask(__name__)
journey_bp = Blueprint('journey_bp', __name__)

@app.route('/add_user_to_journey', methods=['POST'])
def add_user():
    data = request.json
    journey_title = data.get("name")
    user = data.get("users")

    if not journey_title or not user:
        return jsonify({"error": "Missing journey_title or user in request body"}), 400

    return add_user_to_journey(journey_title, user)

@app.route('/view_journeys_of_user', methods=['POST'])
def view_user_journeys():
    data = request.json
    user_name = data.get("users")

    if not user_name:
        return jsonify({"error": "Missing user_name in request body"}), 400

    return view_journeys_of_user(user_name)

@app.route('/view_all_journeys', methods=['POST'])
def view_journeys():
    return view_all_journeys()

@app.route('/create_journey', methods=['POST'])
def create_new_journey():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    return create_journey(data)

@app.route('/update_journey', methods=['POST'])
def update_existing_journey():
    data = request.json
    if not data or "name" not in data or "update_data" not in data:
        return jsonify({"error": "Missing journey_title or update_data in request body"}), 400

    journey_title = data["name"]
    update_data = data["update_data"]

    return update_journey(journey_title, update_data)

@app.route('/delete_journey', methods=['POST'])
def delete_existing_journey():
    data = request.json
    if not data or "name" not in data:
        return jsonify({"error": "Missing journey_title in request body"}), 400

    journey_title = data["name"]

    return delete_journey(journey_title)


@app.route('/view_my_journeys', methods=['POST'])
def view_my_journeys_route():
    data = request.json
    person_name = data.get("person_name")

    if not person_name:
        return jsonify({"error": "Missing person_name in request body"}), 400

    return view_my_journeys(person_name)

@app.route('/track_journey_progress', methods=['POST'])
def track_journey_progress_route():
    data = request.json
    person_name = data.get("person_name")

    if not person_name:
        return jsonify({"error": "Missing person_name in request body"}), 400

    return track_journey_progress(person_name)

@app.route('/complete_task', methods=['POST'])
def complete_task_route():
    data = request.json
    person_name = data.get("person_name")
    journey_title = data.get("journey_title")
    task_name = data.get("task_name")

    if not person_name or not journey_title or not task_name:
        return jsonify({"error": "Missing person_name, journey_title, or task_name in request body"}), 400

    return complete_task(person_name, journey_title, task_name)

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback_route():
    data = request.json
    person_name = data.get("person_name")
    journey_title = data.get("journey_title")
    feedback = data.get("feedback")

    if not person_name or not journey_title or not feedback:
        return jsonify({"error": "Missing person_name, journey_title, or feedback in request body"}), 400

    return submit_feedback(person_name, journey_title, feedback)

@app.route('/view_team_journeys', methods=['POST'])
def view_team_journeys_route():
    data = request.json
    team_member_names = data.get("team_member_names")

    if not team_member_names:
        return jsonify({"error": "Missing team_member_names in request body"}), 400

    return view_team_journeys(team_member_names)

@app.route('/track_team_member_progress', methods=['POST'])
def track_team_member_progress_route():
    data = request.json
    team_member_names = data.get("team_member_names")

    if not team_member_names:
        return jsonify({"error": "Missing team_member_names in request body"}), 400

    return track_team_member_progress(team_member_names)

@app.route('/update_task_status_for_team_member', methods=['POST'])
def update_task_status_for_team_member_route():
    data = request.json
    manager_name = data.get("manager_name")
    team_member_name = data.get("team_member_name")
    journey_title = data.get("journey_title")
    task_name = data.get("task_name")
    status = data.get("status")

    if not manager_name or not team_member_name or not journey_title or not task_name or not status:
        return jsonify({"error": "Missing manager_name, team_member_name, journey_title, task_name, or status in request body"}), 400

    return update_task_status_for_team_member(manager_name, team_member_name, journey_title, task_name, status)

@app.route('/provide_feedback_on_team_member_task', methods=['POST'])
def provide_feedback_on_team_member_task_route():
    data = request.json
    manager_name = data.get("manager_name")
    team_member_name = data.get("team_member_name")
    journey_title = data.get("journey_title")
    task_name = data.get("task_name")
    feedback = data.get("feedback")

    if not manager_name or not team_member_name or not journey_title or not task_name or not feedback:
        return jsonify({"error": "Missing manager_name, team_member_name, journey_title, task_name, or feedback in request body"}), 400

    return provide_feedback_on_team_member_task(manager_name, team_member_name, journey_title, task_name, feedback)

@app.route('/monitor_overall_journey_progress', methods=['POST'])
def monitor_overall_journey_progress_route():
    return monitor_overall_journey_progress()

@app.route('/generate_reports', methods=['POST'])
def generate_reports_route():
    return generate_reports()

if __name__ == '__main__':
    app.run(debug=True, port=5002)
