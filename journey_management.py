# journey_algorithms.py
from datetime import datetime
from pymongo import errors
from general_algo import get_database, data_validation_against_schema

def add_user_to_journey(journey_title, user):
    db = get_database()
    collection = db["JRN_journey"]
    try:
        result = collection.update_one(
            {'name': journey_title},
            {'$addToSet': {'users': user}}
        )

        if result.modified_count == 0:
            return {'error': 'Journey not found or user already added'}, 404
        return {'message': 'User added successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

def view_journeys_of_user(user_name):
    db = get_database()
    collection = db["JRN_journey"]
    try:
        journeys = list(collection.find({'users.person_name': user_name}))
        for journey in journeys:
            journey['_id'] = str(journey['_id'])
        return journeys, 200
    except Exception as e:
        return {'error': str(e)}, 500

def view_all_journeys():
    db = get_database()
    collection = db["JRN_journey"]
    try:
        journeys = list(collection.find({}))
        for journey in journeys:
            journey['_id'] = str(journey['_id'])
        return journeys, 200
    except Exception as e:
        return {'error': str(e)}, 500

def create_journey(data):
    db = get_database()
    collection = db["JRN_journey"]
    try:
        if not data_validation_against_schema(collection, [data]):
            return {'error': 'Data schema does not match collection schema'}, 400

        journey_id = collection.insert_one(data).inserted_id
        return {"message": "Journey created successfully", "journey_id": str(journey_id)}, 201
    except errors.PyMongoError as e:
        return {"error": f"Error inserting data: {e}"}, 500

def update_journey(journey_title, update_data):
    db = get_database()
    collection = db["JRN_journey"]
    try:
        result = collection.update_one(
            {'name': journey_title},
            {'$set': update_data}
        )

        if result.matched_count == 0:
            return {'error': 'Journey not found'}, 404
        return {'message': 'Journey updated successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

def delete_journey(journey_title):
    db = get_database()
    collection = db["JRN_journey"]
    try:
        result = collection.delete_one({'name': journey_title})

        if result.deleted_count == 0:
            return {'error': 'Journey not found'}, 404
        return {'message': 'Journey deleted successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

def view_my_journeys(person_name):
    db = get_database()
    collection = db["JRN_journey"]
    try:
        journeys = list(collection.find({'users.person_name': person_name}))
        for journey in journeys:
            journey['_id'] = str(journey['_id'])
        return journeys, 200
    except Exception as e:
        return {'error': str(e)}, 500

def track_journey_progress(person_name):
    db = get_database()
    collection = db["JRN_journey"]
    try:
        journeys = list(collection.find({'users.person_name': person_name}))
        progress = []
        for journey in journeys:
            completed_tasks = [task for task in journey['tasks'] if task['status'] == 'Completed']
            progress.append({
                'journey': journey['name'],
                'completed_tasks': len(completed_tasks),
                'total_tasks': len(journey['tasks'])
            })
        return progress, 200
    except Exception as e:
        return {'error': str(e)}, 500

def complete_task(person_name, journey_title, task_name):
    db = get_database()
    collection = db["JRN_journey"]
    try:
        result = collection.update_one(
            {'name': journey_title, 'tasks.title': task_name, 'users.person_name': person_name},
            {'$set': {'tasks.$.status': 'Completed'}}
        )

        if result.modified_count == 0:
            return {'error': 'Task not found or already completed'}, 404
        return {'message': 'Task marked as completed'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

def submit_feedback(person_name, journey_title, feedback):
    db = get_database()
    collection = db["JRN_journey"]
    try:
        result = collection.update_one(
            {'name': journey_title, 'users.person_name': person_name},
            {'$set': {'users.$.feedback': feedback}}
        )

        if result.modified_count == 0:
            return {'error': 'Feedback submission failed'}, 404
        return {'message': 'Feedback submitted successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

def view_team_journeys(team_member_names):
    db = get_database()
    collection = db["JRN_journey"]
    try:
        journeys = list(collection.find({'users.person_name': {'$in': team_member_names}}))
        for journey in journeys:
            journey['_id'] = str(journey['_id'])
        return journeys, 200
    except Exception as e:
        return {'error': str(e)}, 500

def track_team_member_progress(team_member_names):
    db = get_database()
    collection = db["JRN_journey"]
    try:
        progress = []
        for name in team_member_names:
            journeys = list(collection.find({'users.person_name': name}))
            for journey in journeys:
                completed_tasks = [task for task in journey['tasks'] if task['status'] == 'Completed']
                progress.append({
                    'team_member': name,
                    'journey': journey['name'],
                    'completed_tasks': len(completed_tasks),
                    'total_tasks': len(journey['tasks'])
                })
        return progress, 200
    except Exception as e:
        return {'error': str(e)}, 500

def update_task_status_for_team_member(manager_name, team_member_name, journey_title, task_name, status):
    db = get_database()
    collection = db["JRN_journey"]
    try:
        result = collection.update_one(
            {'name': journey_title, 'tasks.title': task_name, 'users.person_name': team_member_name},
            {'$set': {'tasks.$.status': status}}
        )

        if result.modified_count == 0:
            return {'error': 'Task not found or status update failed'}, 404
        return {'message': 'Task status updated successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

def provide_feedback_on_team_member_task(manager_name, team_member_name, journey_title, task_name, feedback):
    db = get_database()
    collection = db["JRN_journey"]
    try:
        result = collection.update_one(
            {'name': journey_title, 'tasks.title': task_name, 'users.person_name': team_member_name},
            {'$set': {'tasks.$.manager_feedback': feedback}}
        )

        if result.modified_count == 0:
            return {'error': 'Feedback submission failed'}, 404
        return {'message': 'Feedback submitted successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

def monitor_overall_journey_progress():
    db = get_database()
    collection = db["JRN_journey"]
    try:
        journeys = list(collection.find({}))
        progress = []
        for journey in journeys:
            completed_tasks = [task for task in journey['tasks'] if task['status'] == 'Completed']
            progress.append({
                'journey': journey['name'],
                'completed_tasks': len(completed_tasks),
                'total_tasks': len(journey['tasks'])
            })
        return progress, 200
    except Exception as e:
        return {'error': str(e)}, 500

def generate_reports():
    db = get_database()
    collection = db["JRN_journey"]
    try:
        journeys = list(collection.find({}))
        report = {
            'total_journeys': len(journeys),
            'total_tasks': sum(len(journey['tasks']) for journey in journeys),
            'completed_tasks': sum(task['status'] == 'Completed' for journey in journeys for task in journey['tasks']),
            'feedback': [user.get('feedback', '') for journey in journeys for user in journey['users']]
        }
        return report, 200
    except Exception as e:
        return {'error': str(e)}, 500