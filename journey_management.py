
from datetime import datetime, timedelta
from pymongo import errors, UpdateOne
from flask import jsonify
from general_algo import get_database, data_validation_against_schema,hr_name_fetch
from email_service import send_email
import config
from eligibility import check_employee_eligibility_for_JRN,check_employee_eligibility_for_task

def remove_task_and_cleanup_user(journey_title, person_name, manager_name, action_name):
    db = get_database()
    journey_collection = db[config.JRN_journey]
    employee_collection = db[config.HRM_employee_details]
    try:
        # Step 1: Remove the task that matches the action_name
        result = journey_collection.update_one(
            {
                'name': journey_title,
                'users': {
                    '$elemMatch': {
                        'person_name': manager_name,
                        'tasks.action_name': action_name
                    }
                }
            },
            {
                '$pull': {
                    'users.$.tasks': {
                        'action_name': action_name
                    }
                }
            }
        )

        if result.modified_count > 0:
            print(f"Task with action_name {action_name} removed from {manager_name}'s tasks.")
            manager = employee_collection.find_one({'person_name': manager_name})
            manager_mail = manager.get('email', '')
            print(manager_mail)

            if manager_mail:
                email_data2 = {
                    "to_email": manager_mail,
                    "from_email": config.SMTP_CONFIG['from_email'],
                    "template_name": config['templates']['task_removed_notification'],
                    "data": {
                        "person_name": person_name,
                        "company_name": config.others['company_name'],
                        "tasks": "All tasks in this Journey related to This Employee are removed",
                        "journey_name": journey_title,
                        "manager_name": manager_name,
                        "action_name": action_name
                    }
                }
                send_email(email_data2)
            
            # Step 2: Check if the specific user's task list is now empty
            user_with_empty_tasks = journey_collection.find_one(
                {
                    'name': journey_title,
                    'users': {
                        '$elemMatch': {
                            'person_name': manager_name,
                            'tasks': {'$size': 0}
                        }
                    }
                },
                {
                    'users.$': 1  # Return only the matched user object
                }
            )
            
            if user_with_empty_tasks:
                # Step 3: If no tasks left, remove this specific user object from the users array
                delete_result = journey_collection.update_one(
                    {
                        'name': journey_title,
                        'users.person_name': manager_name,
                        'users.tasks': {'$size': 0}
                    },
                    {
                        '$pull': {
                            'users': {'person_name': manager_name, 'tasks': {'$size': 0}}
                        }
                    }
                )

                if delete_result.modified_count > 0:
                    print(f"{manager_name} has been removed from the journey because they have no tasks left.")
                    return {"message": f"{manager_name} removed from journey as they have no tasks left"}, 200

            return {"message": f"Task with action_name {action_name} removed from {manager_name}'s tasks"}, 200
        else:
            print(f"No tasks removed for {manager_name}.")
            return {"message": f"No tasks removed for {manager_name}"}, 400

    except Exception as e:
        print("Error:", str(e))
        return {"error": str(e)}, 500

def unassign_journey_from_user(journey_title, person_name):
    db = get_database()
    journey_collection = db[config.JRN_journey]
    employee_collection = db[config.HRM_employee_details]

    try:
        # Find the journey and check if the user is assigned to it
        # journey = journey_collection.find_one({'name': journey_title, 'users.person_name': person_name})


        journey = journey_collection.find_one({
            'name': journey_title,
            '$or': [
                {'users.person_name': person_name},
                {'users.tasks.action_name': person_name}
            ]
        })
        if not journey:
            return {'error': f'User {person_name} not found in journey {journey_title}'}, 200

        # Remove the user from the journey
        result = journey_collection.update_one(
            {'name': journey_title},
            {'$pull': {'users': {'person_name': person_name}}}
        )

        if result.modified_count == 0:
            return {'error': 'Failed to unassign the user from the journey'}, 500

        # Get employee email, manager name, and HR name
        employee = employee_collection.find_one({'person_name': person_name})
        if employee:
            employee_email = employee.get('email', '')
            manager_name = employee.get('manager_name', '')
            
            hr_name = hr_name_fetch(employee)
            print(manager_name+" "+hr_name)
            remove_task_and_cleanup_user(journey_title, person_name, manager_name, action_name=person_name)
            remove_task_and_cleanup_user(journey_title, person_name, hr_name, action_name=person_name)

            if employee_email:
                email_data = {
                    "to_email": employee_email,
                    "from_email": config.SMTP_CONFIG['from_email'],
                    "template_name": config['templates']['user_unassigned_from_journey'],
                    "data": {
                        "person_name": person_name,
                        "company_name": config.others['company_name'],
                        "journey_name": journey_title,
                        "manager_name": manager_name,
                        "action_name":person_name
                    }
                }
                send_email(email_data)

        return {'message': f'User {person_name} successfully unassigned from journey {journey_title} and related tasks removed for manager and HR'}, 200

    except Exception as e:
        return {'error': str(e)}, 500


def view_journeys_of_user(person_name):
    db = get_database()
    collection = db[config.JRN_journey]
    employee_collection = db[config.HRM_employee_details]
    
    try:
        # Find the employee in the employee collection
        employee = employee_collection.find_one({'person_name': person_name})
        if not employee:
            return {'error': 'Employee not found'}, 404

        grade = employee.get('grade', '')

        # Find journeys where the person is either in users or team members
        journeys = list(collection.find({'$or': [{'users.person_name': person_name}, {'teams.teammembers.person_name': person_name}]}))
        for journey in journeys:
            journey['_id'] = str(journey['_id'])

            # Filter users in the journey to include only the specified person
        
            journey['users'] = [user for user in journey.get('users', []) if user.get('person_name') == person_name]

            # Filter teams in the journey to include only teams where the specified person is a team member
            journey['teams'] = [team for team in journey.get('teams', []) if any(member.get('person_name') == person_name for member in team.get('teammembers', []))]
            for team in journey['teams']:
                team['teammembers'] = [member for member in team.get('teammembers', []) if member.get('person_name') == person_name]

        return journeys, 200
    except Exception as e:
        return {'error': str(e)}, 500





def view_journey_by_name(journey_name):
    db = get_database()
    collection = db[config.JRN_journey]
    try:
        journey = collection.find_one({'name': journey_name})
        if journey:
            journey['_id'] = str(journey['_id'])
            return journey, 200
        else:
            return {'error': 'Journey not found'}, 404
    except Exception as e:
        return {'error': str(e)}, 500

def track_one_journey_progress(journey_name):
    db = get_database()
    collection = db[config.JRN_journey]
    try:
        journey = collection.find_one({'name': journey_name})
        if journey:
            total_tasks = 0
            completed_tasks = 0
            for user in journey['users']:
                total_tasks += len(user['tasks'])
                completed_tasks += len([task for task in user['tasks'] if task['status'] == 'Completed'])

            team_total_tasks = 0
            team_completed_tasks = 0
            for team in journey.get('teams', []):
                for member in team.get('teammembers', []):
                    team_total_tasks += len(member['tasks'])
                    team_completed_tasks += len([task for task in member['tasks'] if task['status'] == 'Completed'])

            progress = {
                'journey': journey['name'],
                'completed_tasks': completed_tasks,
                'total_tasks': total_tasks,
                'team_completed_tasks': team_completed_tasks,
                'team_total_tasks': team_total_tasks,
                'progress': (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0,
                'team_progress': (team_completed_tasks / team_total_tasks) * 100 if team_total_tasks > 0 else 0
            }
            return progress, 200
        else:
            return {'error': 'Journey not found'}, 404
    except Exception as e:
        return {'error': str(e)}, 500

def create_journey(data):
    db = get_database()
    collection = db[config.JRN_journey]
    try:
        data.pop('users', None)
        data.pop('teams', None)
        if 'users' not in data:
            data['users'] = []
        if 'teams' not in data:
            data['teams'] = []

        if 'tasks' not in data:
            data['tasks'] = []
        if 'created_at' not in data:
            data['created_at'] = datetime.now().strftime('%Y-%m-%d')
        if 'updated_at' not in data:
            data['updated_at'] = datetime.now().strftime('%Y-%m-%d')
        if 'created_by' not in data:
            data['created_by'] = ''

        if not data_validation_against_schema(collection, [data]):
            return {'error': 'Data schema does not match collection schema'}, 400

        journey_id = collection.insert_one(data).inserted_id
        return {"message": "Journey created successfully", "journey_id": str(journey_id)}, 201
    except errors.PyMongoError as e:
        return {"error": f"Error inserting data: {e}"}, 500

def update_journey(journey_title, update_data):
    db = get_database()
    collection = db[config.JRN_journey]
    employee_collection = db[config.HRM_employee_details]
    
    try:
        update_data['updated_at'] = datetime.now().strftime('%Y-%m-%d')
        updated_by = update_data.get('updated_by', 'System')  # Assuming you pass 'updated_by' in update_data

        result = collection.update_one(
            {'name': journey_title},
            {'$set': update_data}
        )

        if result.matched_count == 0:
            return {'error': 'Journey not found'}, 404

        # Fetch the journey after update
        journey = collection.find_one({'name': journey_title})
        users = journey.get('users', [])

        # Notify each user in the journey
        for user in users:
            employee = employee_collection.find_one({'person_name': user['person_name']})
            tasks = user.get('tasks', [])
            action_name = user['person_name']
            for task in tasks:
                    action_name = task.get('action_name', user['person_name'])
            if employee:
                employee_email = employee.get('email', '')
                # print(employee_email)
                if employee_email:
                    email_data = {
                        "to_email": employee_email,
                        "from_email": config.SMTP_CONFIG['from_email'],
                        "template_name": config['templates']['journey_updated'],  # Ensure this template exists in your email template collection
                        "data": {
                            "person_name": user['person_name'],
                            "journey_name": journey_title,
                            "updated_at": update_data['updated_at'],
                            "company_name": config.others['company_name'],
                            "action_name":action_name
                        }
                    }
                    send_email(email_data)

        return {'message': 'Journey updated successfully and notifications sent'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

def delete_journey(journey_title):
    db = get_database()
    collection = db[config.JRN_journey]
    eligibility_profile_collection = db[config.JRN_eligibility_profiles]
    try:
        result = collection.delete_one({'name': journey_title})

        if result.deleted_count == 0:
            return {'error': 'Journey not found'}, 404
       
        journey_eligibility_result = eligibility_profile_collection.delete_many({
            'eligibility_profile_definition.profile_type': 'journey',
            'eligibility_profile_definition.profile_usage': journey_title
        })

        
        return {'message': 'Journey deleted successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

def track_journey_progress():
    db = get_database()
    collection = db[config.JRN_journey]
    try:
        journeys = list(collection.find({}))
        progress = []
        for journey in journeys:
            total_tasks = 0
            completed_tasks = 0
            for user in journey['users']:
                total_tasks += len(user['tasks'])
                completed_tasks += len([task for task in user['tasks'] if task['status'] == 'Completed'])

            team_total_tasks = 0
            team_completed_tasks = 0
            for team in journey.get('teams', []):
                for member in team.get('teammembers', []):
                    team_total_tasks += len(member['tasks'])
                    team_completed_tasks += len([task for task in member['tasks'] if task['status'] == 'Completed'])

            journey_progress = {
                'journey': journey['name'],
                'completed_tasks': completed_tasks,
                'total_tasks': total_tasks,
                'team_completed_tasks': team_completed_tasks,
                'team_total_tasks': team_total_tasks,
                'progress': (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0,
                'team_progress': (team_completed_tasks / team_total_tasks) * 100 if team_total_tasks > 0 else 0
            }
            progress.append(journey_progress)
        return progress, 200
    except Exception as e:
        return {'error': str(e)}, 500

def submit_feedback(person_name, journey_title, task_name, action_name, feedback):
    db = get_database()
    collection = db[config.JRN_journey]
    try:
        # Find the journey and ensure the user with the specific action_name is part of it
        journey = collection.find_one({
            'name': journey_title,
            'users': {
                '$elemMatch': {
                    'person_name': person_name,
                    'tasks.action_name': action_name
                }
            }
        })
        # print(person_name+action_name)

        if not journey:
            return {'error': 'Journey or user not found'}, 404

        # Ensure the user exists in the journey with the correct action_name
        user = next(
            (user for user in journey.get('users', []) 
             if user.get('person_name') == person_name and 
                any(task.get('action_name') == action_name for task in user.get('tasks', []))
            ), 
            None
        )
        
        if not user:
            return {'error': 'User not found in the journey'}, 404

        # Ensure the task exists for the user with the correct action_name
        task = next(
            (task for task in user.get('tasks', []) 
             if task.get('task_name') == task_name and task['action_name'] == action_name), 
            None
        )
        
        if not task:
            return {'error': 'Task not found'}, 404

        if task['feedback'] == feedback:
            return {'message': 'Feedback has already been submitted'}, 200

        # Update the feedback for the task
        result = collection.update_one(
            {
                'name': journey_title,
                'users.person_name': person_name,
                'users.tasks.task_name': task_name,
                'users.tasks.action_name': action_name
            },
            {
                '$set': {
                    'users.$[user].tasks.$[task].feedback': feedback
                }
            },
            array_filters=[
                {'user.person_name': person_name},
                {'task.task_name': task_name, 'task.action_name': action_name}
            ]
        )

        if result.modified_count == 0:
            return {'error': 'Failed to submit feedback'}, 500

        return {'message': 'Feedback submitted successfully'}, 200

    except Exception as e:
        return {'error': str(e)}, 500



def provide_feedback_on_team_member_task(team_name, member_name, journey_title, task_name, feedback, action_name):
    db = get_database()
    collection = db[config.JRN_journey]
    try:
        # Find the journey and ensure the team member with the specific action_name is part of it
        journey = collection.find_one({
            'name': journey_title,
            'teams.team_name': team_name,
            'teams.teammembers': {
                '$elemMatch': {
                    'person_name': member_name,
                    'tasks.action_name': action_name
                }
            }
        })
        if not journey:
            return {'error': 'Journey, team, or member not found'}, 404

        # Ensure the team and member exist in the journey with the correct action_name
        team = next((team for team in journey.get('teams', []) 
                     if team.get('team_name') == team_name), None)
        if not team:
            return {'error': 'Team not found'}, 404

        member = next((member for member in team.get('teammembers', []) 
                       if member.get('person_name') == member_name and 
                          any(task.get('action_name') == action_name for task in member.get('tasks', []))
                      ), None)
        if not member:
            return {'error': 'Team member not found'}, 404

        # Ensure the task exists for the team member with the correct action_name
        task = next((task for task in member.get('tasks', []) 
                     if task.get('task_name') == task_name and task['action_name'] == action_name), 
                    None)
        if not task:
            return {'error': 'Task not found'}, 404

        # Check if the feedback is already the same
        if task.get('feedback') == feedback:
            return {'error': 'Same feedback already submitted'}, 400

        # Update the feedback for the task using the action_name
        result = collection.update_one(
            {
                'name': journey_title,
                'teams.team_name': team_name,
                'teams.teammembers.person_name': member_name,
                'teams.teammembers.tasks.task_name': task_name,
                'teams.teammembers.tasks.action_name': action_name
            },
            {
                '$set': {
                    'teams.$[team].teammembers.$[member].tasks.$[task].feedback': feedback
                }
            },
            array_filters=[
                {'team.team_name': team_name},
                {'member.person_name': member_name},
                {'task.task_name': task_name, 'task.action_name': action_name}
            ]
        )

        if result.modified_count == 0:
            return {'error': 'Failed to update feedback'}, 500

        return {'message': 'Feedback submitted successfully'}, 200

    except Exception as e:
        return {'error': str(e)}, 500



def view_team_journeys(team_name):
    db = get_database()
    collection = db[config.JRN_journey]
    try:
        journeys = list(collection.find({'teams.team_name': team_name}))
        filtered_journeys = []
        for journey in journeys:
            journey['_id'] = str(journey['_id'])
            filtered_teams = [team for team in journey['teams'] if team['team_name'] == team_name]
            journey['teams'] = filtered_teams
            if 'users' in journey:
                del journey['users']
            filtered_journeys.append(journey)
        return filtered_journeys, 200
    except Exception as e:
        return {'error': str(e)}, 500

def track_team_member_progress(team_name, member_name):
    db = get_database()
    collection = db[config.JRN_journey]
    employee_collection = db[config.HRM_employee_details]
    try:
        employee = employee_collection.find_one({'person_name': member_name})
        if not employee:
            return {'error': 'Employee not found'}, 404

        grade = employee.get('grade', '')

        journeys = list(collection.find({'teams.team_name': team_name, f'teams.teammembers.person_name': member_name}))
        progress = []
        for journey in journeys:
            team = next(team for team in journey['teams'] if team['team_name'] == team_name)
            member = next(member for member in team['teammembers'] if member['person_name'] == member_name)
            completed_tasks = len([task for task in member['tasks'] if task['status'] == 'Completed' and task.get('performer') == grade])
            total_tasks = len([task for task in member['tasks'] if task.get('performer') == grade])
            progress.append({
                'team_member': member_name,
                'journey': journey['name'],
                'completed_tasks': completed_tasks,
                'total_tasks': total_tasks,
                'progress': (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
            })
        return progress, 200
    except Exception as e:
        return {'error': str(e)}, 500

def update_task_status_for_team_member(team_name, member_name, journey_title, task_name, action_name):
    db = get_database()
    collection = db[config.JRN_journey]
    employee_collection = db[config.HRM_employee_details]
    try:
        status = "Completed"
        
        # Find the journey and ensure the team member with the specific action_name is part of it
        journey = collection.find_one({
            'name': journey_title,
            'teams.team_name': team_name,
            'teams.teammembers': {
                '$elemMatch': {
                    'person_name': member_name,
                    'tasks.action_name': action_name
                }
            }
        })
        if not journey:
            return {'error': 'Journey, team, or member not found'}, 404

        # Ensure the team and member exist in the journey with the correct action_name
        team = next((team for team in journey.get('teams', []) 
                     if team.get('team_name') == team_name), None)
        if not team:
            return {'error': 'Team not found'}, 404

        member = next((member for member in team.get('teammembers', []) 
                       if member.get('person_name') == member_name and 
                          any(task.get('action_name') == action_name for task in member.get('tasks', []))
                      ), None)
        if not member:
            return {'error': 'Team member not found'}, 404

        # Ensure the task exists for the team member with the correct action_name
        task = next((task for task in member.get('tasks', []) 
                     if task.get('task_name') == task_name and task['action_name'] == action_name), 
                    None)
        if not task:
            return {'error': 'Task not found'}, 404

        # Calculate time status
        due_date = datetime.strptime(task['task_due_date'], '%Y-%m-%d')
        current_date = datetime.now()
        time_status = "Completed on time" if current_date <= due_date else f"Completed {current_date - due_date} day(s) late"

        # Update the task status using the member's person_name and action_name
        result = collection.update_one(
            {
                'name': journey_title,
                'teams.team_name': team_name,
                'teams.teammembers.person_name': member_name,
                'teams.teammembers.tasks.task_name': task_name,
                'teams.teammembers.tasks.action_name': action_name
            },
            {
                '$set': {
                    'teams.$[team].teammembers.$[member].tasks.$[task].status': status,
                    'teams.$[team].teammembers.$[member].tasks.$[task].time_status': time_status
                }
            },
            array_filters=[
                {'team.team_name': team_name},
                {'member.person_name': member_name},
                {'task.task_name': task_name, 'task.action_name': action_name}
            ]
        )

        if result.modified_count == 0:
            return {'error': 'Task status is already completed or failed to update'}, 404

        # Retrieve the employee's email and manager name for notification
        employee = employee_collection.find_one({'person_name': member_name})
        if not employee:
            return {'error': 'Employee not found'}, 404

        employee_email = employee.get('email', '')
        manager_name1 = employee.get('manager_name', '')

        # Send email notification
        email = {
            "to_email": employee_email,
            "from_email": config.SMTP_CONFIG['from_email'],
            "template_name": config['templates']['team_task_complete'],
            "data": {
                "person_name": member_name,
                "team_name": team_name,
                "task_name": task_name,
                "completion_date": current_date.strftime('%B %d, %Y'),
                "task_status": time_status,
                "manager_name": manager_name1,
                "action_name": task['action_name'],
                "journey_title": journey_title
            }
        }
        # Uncomment to send the email
        send_email(email)

        return {'message': 'Task status updated successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500


def monitor_overall_journey_progress():
    db = get_database()
    collection = db[config.JRN_journey]
    try:
        journeys = list(collection.find({}))
        progress = []
        for journey in journeys:
            completed_tasks = 0
            total_tasks = 0

            for user in journey.get('users', []):
                user_tasks = user.get('tasks', [])
                completed_tasks += len([task for task in user_tasks if task.get('status') == 'Completed'])
                total_tasks += len(user_tasks)

            team_completed_tasks = 0
            team_total_tasks = 0
            for team in journey.get('teams', []):
                for member in team.get('teammembers', []):
                    member_tasks = member.get('tasks', [])
                    team_completed_tasks += len([task for task in member_tasks if task.get('status') == 'Completed'])
                    team_total_tasks += len(member_tasks)

            progress.append({
                'journey': journey.get('name', 'Unknown'),
                'completed_tasks': completed_tasks,
                'total_user_tasks': total_tasks,
                'team_completed_tasks': team_completed_tasks,
                'team_total_tasks': team_total_tasks,
                'progress': (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0,
                'team_progress': (team_completed_tasks / team_total_tasks) * 100 if team_total_tasks > 0 else 0
            })
        return progress, 200
    except Exception as e:
        return {'error': str(e)}, 500

def generate_reports():
    db = get_database()
    collection = db[config.JRN_journey]
    try:
        journeys = list(collection.find({}))
        report = []
        for journey in journeys:
            journey_report = {
                'journey_name': journey.get('name', 'Unknown'),
                'users': [],
                'teams': []
            }

            # Ensure all users are printed
            users = journey.get('users', [])
            if isinstance(users, list):
                for user in users:
                    total_tasks = len(user.get('tasks', []))
                    completed_tasks = len([task for task in user.get('tasks', []) if task['status'] == 'Completed'])
                    progress = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
                    journey_report['users'].append({
                        'person_name': user.get('person_name', 'Unknown'),
                        'progress': progress,
                        'completed_tasks': completed_tasks,
                        'total_tasks': total_tasks
                    })

            # Ensure all teams and team members are printed
            teams = journey.get('teams', [])
            if isinstance(teams, list):
                for team in teams:
                    team_progress = {}
                    team_members = team.get('teammembers', [])
                    if isinstance(team_members, list):
                        for member in team_members:
                            total_tasks = len(member.get('tasks', []))
                            completed_tasks = len([task for task in member.get('tasks', []) if task['status'] == 'Completed'])
                            progress = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
                            team_progress[member.get('person_name', 'Unknown')] = {
                                'progress': progress,
                                'completed_tasks': completed_tasks,
                                'total_tasks': total_tasks
                            }
                    journey_report['teams'].append({
                        'team_name': team.get('team_name', 'Unknown'),
                        'progress': team_progress
                    })

            report.append(journey_report)
        return report, 200
    except Exception as e:
        return {'error': str(e)}, 500


def view_my_journeys(person_name):
    db = get_database()
    collection = db[config.JRN_journey]
    employee_collection = db[config.HRM_employee_details]
    
    try:
        # Find the employee in the employee collection
        employee = employee_collection.find_one({'person_name': person_name})
        if not employee:
            return {'error': 'Employee not found'}, 404

        grade = employee.get('grade', '')

        # Find journeys where the person is either in users or team members
        journeys = list(collection.find({'$or': [{'users.person_name': person_name}, {'teams.teammembers.person_name': person_name}]}))
        for journey in journeys:
            journey['_id'] = str(journey['_id'])

            # Filter users in the journey to include only the specified person
            if 'tasks' in journey:
                del journey['tasks']
            journey['users'] = [user for user in journey.get('users', []) if user.get('person_name') == person_name]

            # Filter teams in the journey to include only teams where the specified person is a team member
            journey['teams'] = [team for team in journey.get('teams', []) if any(member.get('person_name') == person_name for member in team.get('teammembers', []))]
            for team in journey['teams']:
                team['teammembers'] = [member for member in team.get('teammembers', []) if member.get('person_name') == person_name]

        return journeys, 200
    except Exception as e:
        return {'error': str(e)}, 500


def add_user_to_team_in_journey(journey_title, team_name, member_name):
    db = get_database()
    collection = db[config.JRN_journey]
    task_collection = db[config.JRN_task]
    employee_collection = db[config.HRM_employee_details]

    try:
        # Fetch the journey details
        journey = collection.find_one({'name': journey_title})
        if not journey:
            return {'error': 'Journey not found'}, 404

        # Fetch the employee details
        employee = employee_collection.find_one({'person_name': member_name})
        if not employee:
            return {'error': 'Employee not found'}, 404


        # If an eligibility profile exists, check journey eligibility for the employee
        if not check_employee_eligibility_for_JRN(member_name, journey_title):
            return {'error': f'Employee {member_name} is not eligible for journey {journey_title}'}, 403


        # Check if the team exists and if the user is already part of the team
        team = next((team for team in journey.get('teams', []) if team['team_name'] == team_name), None)
        if not team:
            return {'error': 'Team not found in the journey'}, 404

        # Check if the user is already added to the team in the journey
        existing_user = next(
            (member for member in team.get('teammembers', [])
             if member['person_name'] == member_name and
             any(task['action_name'] == member_name for task in member.get('tasks', []))),
            None
        )
        if existing_user:
            return {'message': 'User is already added to this team in the journey'}, 200

        grade = employee.get('grade', '')
        manager_name = employee.get('manager_name', '')
        hr_name = hr_name_fetch(employee)
        print(hr_name)

        # Initialize task lists for employee, manager, and HR
        tasks_for_employee = []
        tasks_for_manager = []
        tasks_for_hr = []

        # Assign tasks based on performer
        for task_name in journey['tasks']:
            task_info = task_collection.find_one({'task_name': task_name})
            if not task_info:
                return {'error': f'Task {task_name} not found in task collection'}, 404
            
            task_due_date = datetime.now() + timedelta(days=task_info['duration'])

            # If an eligibility profile exists, check task eligibility for the employee
            if not check_employee_eligibility_for_task(member_name, task_name):
                print(f"Employee {member_name} is not eligible for task {task_name}")
                continue  # Skip the task if the employee is not eligible

            # Assign tasks to the employee
            if task_info.get('performer').lower() == "employee":
                tasks_for_employee.append({
                    "task_name": task_name,
                    "status": "Not Started",
                    "task_start_date": datetime.now().strftime('%Y-%m-%d'),
                    "task_due_date": task_due_date.strftime('%Y-%m-%d'),
                    "time_status": "On time",
                    "feedback": "",
                    "performer": task_info.get('performer'),
                    "action_name": member_name  # Use member_name as action_name
                })

            # Assign tasks to the manager
            if manager_name and task_info.get('performer').lower() == "manager":
                tasks_for_manager.append({
                    "task_name": task_name,
                    "status": "Not Started",
                    "task_start_date": datetime.now().strftime('%Y-%m-%d'),
                    "task_due_date": task_due_date.strftime('%Y-%m-%d'),
                    "time_status": "On time",
                    "feedback": "",
                    "performer": "Manager",
                    "action_name": member_name  # Use member_name as action_name for manager
                })

            # Assign tasks to the HR representative
            if hr_name and task_info.get('performer').lower() == "hr":
                tasks_for_hr.append({
                    "task_name": task_name,
                    "status": "Not Started",
                    "task_start_date": datetime.now().strftime('%Y-%m-%d'),
                    "task_due_date": task_due_date.strftime('%Y-%m-%d'),
                    "time_status": "On time",
                    "feedback": "",
                    "performer": "HR",
                    "action_name": member_name  # Use member_name as action_name for HR
                })

        # Add the employee to the team in the journey
        result = collection.update_one(
            {'name': journey_title, 'teams.team_name': team_name},
            {'$addToSet': {'teams.$.teammembers': {
                'person_name': member_name,
                'status': 'In Progress',
                'tasks': tasks_for_employee
            }}}
        )

       

        # Add manager and HR to the journey with their tasks
        if manager_name:
            collection.update_one(
               {'name': journey_title, 'teams.team_name': team_name},
               {'$addToSet': {'teams.$.teammembers': {
                    'person_name': manager_name,
                    'status': 'In Progress',
                    'tasks': tasks_for_manager
                }}}
            )

        if hr_name:
            collection.update_one(
              {'name': journey_title, 'teams.team_name': team_name},
              {'$addToSet': {'teams.$.teammembers': {
                    'person_name': hr_name,
                    'status': 'In Progress',
                    'tasks': tasks_for_hr
                }}}
            )

        # Prepare and send the email to the employee
        if employee.get('email'):
            send_email({
                "to_email": employee['email'],
                "from_email": config.SMTP_CONFIG['from_email'],
                "template_name": config['templates']['team_assignment_notification'],
                "data": {
                    "person_name": member_name,
                    "team_name": team_name,
                    "journey_name": journey_title,
                    "action_name": member_name,  # Use member_name as action_name
                    "task_list": "".join(f"<li>{task['task_name']} (Due: {task['task_due_date']})</li>" for task in tasks_for_employee),
                    "company_name": config.others['company_name'],
                 
                }
            })

        # Prepare and send the email to the manager
        if manager_name and manager_name != member_name:
            manager = employee_collection.find_one({'person_name': manager_name})
            if manager and manager.get('email'):
                send_email({
                    "to_email": manager['email'],
                    "from_email": config.SMTP_CONFIG['from_email'],
                    "template_name": config['templates']['team_assignment_notification'],
                    "data": {
                        "person_name": manager_name,
                        "team_name": team_name,
                        "journey_name": journey_title,
                        "action_name": member_name,  # Use member_name as action_name for manager
                        "task_list": "".join(f"<li>{task['task_name']} (Due: {task['task_due_date']})</li>" for task in tasks_for_manager),
                        "company_name": config.others['company_name']
                    }
                })

        # Prepare and send the email to the HR representative
        if hr_name and hr_name != member_name:
            hr = employee_collection.find_one({'person_name': hr_name})
            if hr and hr.get('email'):
                send_email({
                    "to_email": hr['email'],
                    "from_email": config.SMTP_CONFIG['from_email'],
                    "template_name": config['templates']['team_assignment_notification'],
                    "data": {
                        "person_name": hr_name,
                        "team_name": team_name,
                        "journey_name": journey_title,
                        "action_name": member_name,  # Use member_name as action_name for HR
                        "task_list": "".join(f"<li>{task['task_name']} (Due: {task['task_due_date']})</li>" for task in tasks_for_hr),
                        "company_name": config.others['company_name']
                    }
                })

        return {'message': 'User, manager, and HR added to team successfully and notifications sent'}, 200
    except Exception as e:
        return {'error': str(e)}, 500


def create_task(data):
    db = get_database()
    collection = db[config.JRN_task]
    try:
        data.pop("created_at", None)
        data.pop("created_by", None)
        data.pop("updated_at", None)

        data['created_at'] = datetime.now().strftime('%Y-%m-%d')
        data['updated_at'] = datetime.now().strftime('%Y-%m-%d')
        data['created_by'] = datetime.now().strftime('%Y-%m-%d')
        if not data_validation_against_schema(collection, [data]):
            return {'error': 'Data schema does not match collection schema'}, 400
        task_id = collection.insert_one(data).inserted_id
        return {"message": "Task created successfully", "task_id": str(task_id)}, 201
    except errors.PyMongoError as e:
        return {"error": f"Error inserting data: {e}"}, 500

def update_task(task_name, update_data):
    db = get_database()
    task_collection = db[config.JRN_task]
    journey_collection = db[config.JRN_journey]
    employee_collection = db[config.HRM_employee_details]

    try:
        # Update the task in the JRN_task collection
        result = task_collection.update_one(
            {'task_name': task_name},
            {'$set': update_data}
        )

        if result.matched_count == 0:
            return {'error': 'Task not found'}, 404

        # Get the task details
        task = task_collection.find_one({'task_name': task_name})
        if task is None:
            return {'error': f'Task {task_name} not found after update'}, 404
        
        update_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_by = update_data.get('updated_by', 'System')

        # Find all journeys where this task is assigned
        journeys = journey_collection.find({'users.tasks.task_name': task_name})

        for journey in journeys:
            # Notify individual users
            for user in journey['users']:
                user_tasks = [t for t in user.get('tasks', []) if t['task_name'] == task_name]
                
                if user_tasks:
                    person_name = user.get('person_name', None)
                    if not person_name:
                        continue  # Skip if person_name is not available

                    employee = employee_collection.find_one({'person_name': person_name})
                    if employee is None:
                        continue  # Skip if employee record is not found

                    employee_email = employee.get('email', None)
                    if not employee_email:
                        continue  # Skip if employee email is not available

                    # Prepare the email for each user assigned to the task
                    action_name = person_name
                    for task in user_tasks:
                        action_name=task['action_name']

                    email = {
                        "to_email": employee_email,
                        "from_email": config.SMTP_CONFIG['from_email'],
                        "template_name": config['templates']['task_updated'],
                        "data": {
                            "journey_name":journey['name'],
                            "task_name": task_name,
                            "person_name": person_name,
                            "updated_by": updated_by,
                            "update_date": update_date,
                            "company_name": config.others['company_name'],
                            "action_name":action_name
                        }
                    }
                    send_email(email)

            # Notify team members
            for team in journey.get('teams', []):
                for member in team.get('teammembers', []):
                    member_tasks = [t for t in member.get('tasks', []) if t['task_name'] == task_name]

                    if member_tasks:
                        person_name = member.get('person_name', None)
                        if not person_name:
                            continue  # Skip if person_name is not available

                        employee = employee_collection.find_one({'person_name': person_name})
                        if employee is None:
                            continue  # Skip if employee record is not found

                        employee_email = employee.get('email', None)
                        if not employee_email:
                            continue  # Skip if employee email is not available

                        action_name = person_name
                        for task in member_tasks:
                            action_name=task['action_name']


                        # Prepare the email for each team member associated with the task
                        email = {
                            "to_email": employee_email,
                            "from_email": config.SMTP_CONFIG['from_email'],
                            "template_name": config['templates']['task_updated'],
                            "data": {
                                "journey_name":journey['name'],
                                "task_name": task_name,
                                "person_name": person_name,
                                "updated_by": updated_by,
                                "update_date": update_date,
                                "company_name": config.others['company_name'],
                                 "action_name":action_name
                            }
                        }
                        send_email(email)

        return {'message': 'Task updated successfully and notifications sent'}, 200
    except Exception as e:
        return {'error': str(e)}, 500


def view_task(task_name):
    db = get_database()
    collection = db[config.JRN_task]
    try:
        task = collection.find_one({'task_name': task_name})
        if task:
            task['_id'] = str(task['_id'])
            return task, 200
        return {'error': 'Task not found'}, 404
    except Exception as e:
        return {'error': str(e)}, 500

def delete_task(task_name):
    db = get_database()
    collection = db[config.JRN_task]
    eligibility_collection = db[config.JRN_eligibility_profiles]  # Assuming this is the collection for eligibility profiles

    try:
        result = collection.delete_one({'task_name': task_name})

        
        journey_eligibility_result = eligibility_collection.delete_many({
            'eligibility_profile_definition.profile_type': 'journey_task',
            'eligibility_profile_definition.profile_usage': task_name
        })

        if result.deleted_count == 0:
            return {'error': 'Task not found'}, 404
        return {'message': 'Task deleted successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500
    
def show_my_tasks(person_name):
    db = get_database()
    collection = db[config.JRN_journey]
    task_collection = db[config.JRN_task]
    employee_collection = db[config.HRM_employee_details]

    try:
        # Find the employee in the employee collection
        employee = employee_collection.find_one({'person_name': person_name})
        if not employee:
            return {'error': 'Employee not found'}, 404

        grade = employee.get('grade', '')

        tasks = []
        # Fetch journeys where the person is either in users or team members
        journeys = list(collection.find({'$or': [{'users.person_name': person_name}, {'teams.teammembers.person_name': person_name}]}))

        for journey in journeys:
            journey_name = journey.get('name', 'Unknown Journey')

            # Process tasks assigned to the user directly
            for user in journey.get('users', []):
                if user.get('person_name') == person_name:
                    for task in user.get('tasks', []):
                        
                        task_details = task_collection.find_one({'task_name': task.get('task_name')})
                        tasks.append({
                            'task_name': task.get('task_name', 'Unknown Task'),
                            'journey_name': journey_name,
                            'description': task_details.get('description', 'N/A') if task_details else 'N/A',
                            'instructions': task_details.get('instructions', 'N/A') if task_details else 'N/A',
                            'time_status': task.get('time_status', 'N/A'),
                            'status': task.get('status', 'N/A'),
                            'action_name': task.get('action_name', 'N/A')  # Return action_name with tasks
                        })

            # Process tasks assigned to the user as a team member
            for team in journey.get('teams', []):
                for member in team.get('teammembers', []):
                    if member.get('person_name') == person_name:
                        for task in member.get('tasks', []):
                          
                            task_details = task_collection.find_one({'task_name': task.get('task_name')})
                            tasks.append({
                                'task_name': task.get('task_name', 'Unknown Task'),
                                'journey_name': journey_name,
                                'description': task_details.get('description', 'N/A') if task_details else 'N/A',
                                'instructions': task_details.get('instructions', 'N/A') if task_details else 'N/A',
                                'description': f'Team ({team.get("team_name", "Unknown Team")})',
                                'time_status': task.get('time_status', 'N/A'),
                                'status': task.get('status', 'N/A'),
                                'team_name': team.get('team_name', 'Unknown Team'),
                                'action_name': task.get('action_name', 'N/A')  # Return action_name with tasks
                            })

        return tasks, 200

    except Exception as e:
        return {'error': str(e)}, 500

# def show_team_journey_tasks_and_report(team_name, member_name=None):
#     db = get_database()
#     collection = db[config.JRN_journey]
#     try:
#         report = {
#             'tasks': [],
#             'member_report': {}
#         }

#         # Find all journeys that include the specified team
#         journeys = list(collection.find({'teams.team_name': team_name}))

#         for journey in journeys:
#             journey_name = journey['name']
#             team = next((team for team in journey['teams'] if team['team_name'] == team_name), None)

#             if team is None:
#                 continue  # If no team is found, skip this journey

#             # If member_name is provided, filter and show only that member's tasks
#             if member_name:
#                 members = [member for member in team['teammembers'] if member['person_name'] == member_name]
#             else:
#                 members = team['teammembers']

#             # Append tasks for the specific member(s)
#             for member in members:
#                 for task in member['tasks']:
#                     report['tasks'].append({
#                         'journey_name': journey_name,
#                         'task_name': task.get('task_name', 'Unknown Task'),
#                         'status': task.get('status', 'N/A'),
#                         'time_status': task.get('time_status', 'N/A'),
#                         'task_start_date': task.get('task_start_date', 'N/A'),
#                         'task_due_date': task.get('task_due_date', 'N/A'),
#                         'feedback': task.get('feedback', 'N/A'),
#                         'performer': task.get('performer', 'N/A'),
#                         'action_name': task.get('action_name', 'N/A')  # Include action_name
#                     })

#                 # Generate report for all team members
#                 completed_tasks = len([task for task in member['tasks'] if task['status'] == 'Completed'])
#                 pending_tasks = len([task for task in member['tasks'] if task['status'] != 'Completed'])
#                 report['member_report'][member['person_name']] = {
#                     'completed_tasks': completed_tasks,
#                     'pending_tasks': pending_tasks
#                 }

#         return report, 200
#     except Exception as e:
#         return {'error': str(e)}, 500

def show_team_journey_tasks_and_report(team_name, member_name=None):
    db = get_database()
    collection = db[config.JRN_journey]
    try:
        report = {
            'tasks': [],
            'member_report': {}
        }

        # Find all journeys that include the specified team
        journeys = list(collection.find({'teams.team_name': team_name}))

        for journey in journeys:
            journey_name = journey['name']
            team = next((team for team in journey['teams'] if team['team_name'] == team_name), None)

            if team is None:
                continue  # If no team is found, skip this journey

            # If member_name is provided, filter and show only that member's tasks
            if member_name:
                members = [member for member in team['teammembers'] if member['person_name'] == member_name]
            else:
                members = team['teammembers']

            # Append tasks for the specific member(s)
            for member in members:
                for task in member['tasks']:
                    report['tasks'].append({
                        'journey_name': journey_name,
                        'task_name': task.get('task_name', 'Unknown Task'),
                        'status': task.get('status', 'N/A'),
                        'time_status': task.get('time_status', 'N/A'),
                        'task_start_date': task.get('task_start_date', 'N/A'),
                        'task_due_date': task.get('task_due_date', 'N/A'),
                        'feedback': task.get('feedback', 'N/A'),
                        'performer': task.get('performer', 'N/A'),
                        'action_name': task.get('action_name', 'N/A')  # Include action_name
                    })

                # Generate report for all team members

            for member in team['teammembers']:
                completed_tasks = len([task for task in member['tasks'] if task['status'] == 'Completed'])
                pending_tasks = len([task for task in member['tasks'] if task['status'] != 'In Progress'])
                report['member_report'][member['person_name']] = {
                    'completed_tasks': completed_tasks,
                    'pending_tasks': pending_tasks
                }
        return report, 200
    except Exception as e:
        return {'error': str(e)}, 500


def show_journey_activities():
    db = get_database()
    collection = db[config.JRN_journey]
    try:
        activities = []
        journeys = list(collection.find({}))

        for journey in journeys:
            journey_name = journey['name']

            # Initialize default values
            total_assignees = 0
            journey_status = 'Unknown'
            journey_start_date = 'Unknown'
            journey_due_date = 'Unknown'
            journey_time_status = 'Unknown'

            # User Activities
            users = journey.get('users', [])
            if isinstance(users, list):
                total_assignees += len(users)
                if users:
                    first_user = users[0]
                    journey_status = first_user.get('status', 'Unknown')
                    journey_start_date = first_user.get('journey_start_date', 'Unknown')
                    journey_due_date = first_user.get('journey_due_date', 'Unknown')

                    # Determine time status
                    if journey_due_date != 'Unknown':
                        try:
                            due_date = datetime.strptime(journey_due_date, '%Y-%m-%d').date()
                            current_date = datetime.now().date()
                            journey_time_status = 'On time' if current_date <= due_date else f'Overdue by {(current_date - due_date).days} days'
                        except ValueError:
                            journey_time_status = 'Invalid date format'

            # Team Activities
            teams = journey.get('teams', [])
            if isinstance(teams, list):
                total_assignees += sum(len(team.get('teammembers', [])) for team in teams)
                if teams and journey_time_status == 'Unknown':
                    first_team = teams[0]
                    journey_status = first_team.get('status', 'Unknown')
                    journey_start_date = first_team.get('journey_start_date', 'Unknown')
                    journey_due_date = first_team.get('journey_due_date', 'Unknown')

                    # Determine time status
                    if journey_due_date != 'Unknown':
                        try:
                            due_date = datetime.strptime(journey_due_date, '%Y-%m-%d').date()
                            current_date = datetime.now().date()
                            journey_time_status = 'On time' if current_date <= due_date else f'Overdue by {(current_date - due_date).days} days'
                        except ValueError:
                            journey_time_status = 'Invalid date format'

            # Append journey summary to activities
            activities.append({
                'journey_name': journey_name,
                'assignees': total_assignees,
                'status': journey_status,
                'start_date': journey_start_date,
                'due_date': journey_due_date,
                'time_status': journey_time_status
            })

        return activities, 200
    except Exception as e:
        return {'error': str(e)}, 500



def update_time_status():
    db = get_database()
    collection = db[config.JRN_journey]
    try:
        current_date = datetime.now().date()
        updates = []

        journeys = list(collection.find({}))
        for journey in journeys:
            if 'users' in journey and isinstance(journey['users'], list):
                for user_index, user in enumerate(journey['users']):
                    if 'tasks' in user and isinstance(user['tasks'], list):
                        for task_index, task in enumerate(user['tasks']):
                            if isinstance(task, dict) and 'status' in task and task['status'] == 'Completed':
                                continue
                            if isinstance(task, dict) and 'task_due_date' in task and 'task_name' in task:
                                due_date = datetime.strptime(task['task_due_date'], '%Y-%m-%d').date()
                                if current_date <= due_date:
                                    time_status = 'On time'
                                else:
                                    time_status = f'Overdue by {(current_date - due_date).days} days'
                                if 'time_status' in task and task['time_status'] != time_status:
                                    updates.append(UpdateOne(
                                        {'_id': journey['_id'], f'users.{user_index}.tasks.{task_index}.task_name': task['task_name']},
                                        {'$set': {f'users.{user_index}.tasks.{task_index}.time_status': time_status}}
                                    ))

            if 'teams' in journey and isinstance(journey['teams'], list):
                for team_index, team in enumerate(journey['teams']):
                    if 'teammembers' in team and isinstance(team['teammembers'], list):
                        for member_index, member in enumerate(team['teammembers']):
                            if 'tasks' in member and isinstance(member['tasks'], list):
                                for task_index, task in enumerate(member['tasks']):
                                    if isinstance(task, dict) and 'status' in task and task['status'] == 'Completed':
                                        continue
                                    if isinstance(task, dict) and 'task_due_date' in task and 'task_name' in task:
                                        due_date = datetime.strptime(task['task_due_date'], '%Y-%m-%d').date()
                                        if current_date <= due_date:
                                            time_status = 'On time'
                                        else:
                                            time_status = f'Overdue by {(current_date - due_date).days} days'
                                        if 'time_status' in task and task['time_status'] != time_status:
                                            updates.append(UpdateOne(
                                                {'_id': journey['_id'], f'teams.{team_index}.teammembers.{member_index}.tasks.{task_index}.task_name': task['task_name']},
                                                {'$set': {f'teams.{team_index}.teammembers.{member_index}.tasks.{task_index}.time_status': time_status}}
                                            ))

        if updates:
            collection.bulk_write(updates)
        return {'message': 'Time statuses updated successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500
    
def add_team(journey_name, team_data):
    db = get_database()
    collection = db[config.JRN_journey]

    try:
        journey = collection.find_one({'name': journey_name})
        if not journey:
            return {'error': 'Journey not found'}, 404

        # Check if the team already exists within the journey
        existing_team = next((team for team in journey.get('teams', []) if team['team_name'] == team_data["team_name"]), None)
        if existing_team:
            return {'message': f'Team {team_data["team_name"]} already exists in the journey'}, 200

        # Create the team structure in the journey
        result = collection.update_one(
            {'name': journey_name},
            {'$addToSet': {
                'teams': {
                    'team_name': team_data["team_name"],
                    'journey_start_date': team_data["journey_start_date"],
                    'journey_due_date': team_data["journey_due_date"],
                    'status': team_data["status"],
                    'teammembers': []  # Initialize with an empty list of team members
                }
            }}
        )

        if result.modified_count == 0:
            return {'error': 'Failed to create the team'}, 500

        # Add each team member using the add_user_to_team_in_journey function
        not_eligible=[]
        for member in team_data["teammembers"]:
            print(journey_name+team_data["team_name"]+ member['person_name'])
            response, status_code = add_user_to_team_in_journey(journey_name, team_data["team_name"], member['person_name'])
            if status_code != 200:
                not_eligible.append(member['person_name'])
                # return {'error': f'Failed to add {member["person_name"]} to the team'}, status_code

        if not_eligible:
            return {'error': f'The following employees could not be added due to already added or eligibility failure: {", ".join(not_eligible)} Team is made and other users are added'}, 400

        return {'message': 'Team and users added successfully'}, 200

    except Exception as e:
        return {'error': str(e)}, 500


def view_all_journeys():
    try:
        db = get_database()
        
        journey_collection = db[config.JRN_journey]
        journeys = list(journey_collection.find({}, {'name': 1, 'category': 1, '_id': 0}))
        return journeys, 200
    except Exception as e:
        return {'error': str(e)}, 500

def add_employee(employee_details):
    db = get_database()
    employee_collection = db[config.HRM_employee_details]
    print("running")
    try:
        person_name = employee_details["person_name"]
        grade = employee_details.get("grade", "").lower()
        email_address = employee_details.get("email", "")
        employement_type =  employee_details.get("employment_type","").lower()
        
        if 'created_at' not in employee_details:
            employee_details['created_at'] = datetime.now().strftime('%Y-%m-%d')
        if 'updated_at' not in employee_details:
            employee_details['updated_at'] = datetime.now().strftime('%Y-%m-%d')
        if 'created_by' not in employee_details:
            employee_details['created_by'] = ''

        result = employee_collection.insert_one(employee_details)

        # Assign the employee to pre-onboarding journeys
        journeys, status_code = view_all_journeys()
        if status_code != 200:
            return journeys, status_code

        for journey in journeys:
            category = journey['category']
            if category == config.JRN_boarding_category['pre_onboarding_category']:
                journey_response, status_code = add_user_to_journey(journey['name'], {'person_name': person_name})

        # Send email notification to the new employee
      
        email = {
            "to_email": email_address,
            "from_email": config.SMTP_CONFIG['from_email'],  # Replace with your email
            "template_name": config['templates']['employee_added_notification'],
            "data": {
                "person_name": person_name,
                "grade": grade,
                "created_at": employee_details['created_at'],
                "company_name":config.others['company_name'],
                "action_name":person_name
            }
        }
        send_email(email)

        return {"message": "Employee added successfully", "employee_id": str(result.inserted_id)}, 201
    except Exception as e:
        return {"error": str(e)}, 500

def complete_task(person_name, journey_title, task_name, action_name):
    db = get_database()
    collection = db[config.JRN_journey]
    employee_collection = db[config.HRM_employee_details]
    try:
        # Find the journey and ensure the user with the specific action_name is part of it
        journey = collection.find_one({
            'name': journey_title,
            'users': {
                '$elemMatch': {
                    'person_name': person_name,
                    'tasks.action_name': action_name
                }
            }
        })
        
        if not journey:
            return {'error': 'Journey or user not found'}, 404

        # Ensure the user exists in the journey with the correct action_name
        user = next(
            (user for user in journey.get('users', []) 
             if user.get('person_name') == person_name and 
                any(task.get('action_name') == action_name for task in user.get('tasks', []))
            ), 
            None
        )
        
        if not user:
            return {'error': 'User not found in the journey'}, 404

        # Ensure the task exists for the user with the correct action_name
        task = next(
            (task for task in user.get('tasks', []) 
             if task.get('task_name') == task_name and task['action_name'] == action_name), 
            None
        )
        
        if not task:
            return {'error': 'Task not found'}, 404

        # Calculate time status
        due_date = datetime.strptime(task['task_due_date'], '%Y-%m-%d')
        current_date = datetime.now()
        time_status = "Completed on time" if current_date <= due_date else f"Completed {current_date - due_date} day(s) late"

        # Update the task status using the user's person_name and action_name
        result = collection.update_one(
            {
                'name': journey_title,
                'users.person_name': person_name,
                'users.tasks.task_name': task_name,
                'users.tasks.action_name': action_name
            },
            {
                '$set': {
                    'users.$[user].tasks.$[task].status': 'Completed',
                    'users.$[user].tasks.$[task].time_status': time_status
                }
            },
            array_filters=[
                {'user.person_name': person_name},
                {'task.task_name': task_name, 'task.action_name': action_name}
            ]
        )

        if result.modified_count == 0:
            return {'error': 'Task is already mark completed'}, 500
        
        # Retrieve the employee's email and manager name for notification
        employee = employee_collection.find_one({'person_name': person_name})
        if not employee:
            return {'error': 'Employee not found'}, 404
        
        employee_email = employee.get('email', '')
        manager_name1 = employee.get('manager_name', '')

        # Send email notification
        email = {
            "to_email": employee_email,
            "from_email": config.SMTP_CONFIG['from_email'],
            "template_name": config['templates']['task_complete'],
            "data": {
                "journey_title":journey_title,
                "person_name": person_name,
                "task_name": task_name,
                "completion_date": current_date.strftime('%B %d, %Y'),  # Format the date
                "task_status": time_status,
                "manager_name": manager_name1,
                "action_name":action_name,
                "company_name":config.others['company_name']
            }
        }
        # Uncomment to send the email
        send_email(email)

        return {'message': 'Task marked as completed'}, 200

    except Exception as e:
        return {'error': str(e)}, 500

    

def update_status_for_completed_tasks():
    db = get_database()
    collection = db[config.JRN_journey]

    try:
        # Fetch all journeys
        journeys = list(collection.find({}))

        for journey in journeys:
            # Check for users
            if 'users' in journey and isinstance(journey['users'], list):
                for user in journey['users']:
                    tasks = user.get('tasks', [])
                    if tasks and all(task['status'] == 'Completed' for task in tasks):
                        user['status'] = 'Completed'
                    else:
                        user['status'] = 'In Progress'
                # Update the journey with the new user status
                collection.update_one(
                    {'_id': journey['_id']},
                    {'$set': {'users': journey['users']}}
                )

            # Check for teams
            if 'teams' in journey and isinstance(journey['teams'], list):
                for team in journey['teams']:
                    for member in team.get('teammembers', []):
                        tasks = member.get('tasks', [])
                        if tasks and all(task['status'] == 'Completed' for task in tasks):
                            member['status'] = 'Completed'
                        else:
                            member['status'] = 'In Progress'
                    # Update the journey with the new team member status
                    collection.update_one(
                        {'_id': journey['_id']},
                        {'$set': {'teams': journey['teams']}}
                    )

        return {'message': 'Statuses updated successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500


def assign_onboarding_journeys_for_today():
    db = get_database()
    employee_collection = db[config.HRM_employee_details]
    task_collection = db[config.JRN_task] 
    today = datetime.now().strftime('%Y-%m-%d')

    # Find unique employees with today's start date
    employees = list(employee_collection.aggregate([
        {'$match': {'effective_start_date': today}},
        {'$group': {'_id': '$person_name', 'employee_data': {'$first': '$$ROOT'}}}
    ]))
   
    if not employees:
        return {"message": "No employees found with today's start date"}, 200

    journey_collection = db[config.JRN_journey]
    journeys = list(journey_collection.find({}, {'name': 1, 'category': 1, '_id': 0}))

    # Iterate through unique employees
    for employee_entry in employees:
        employee = employee_entry['employee_data']
        person_name = employee["person_name"]
        employment_type = employee["employment_type"].lower()
        grade = employee.get('grade', '')
        employee_email = employee.get('email', '')
        manager_name = employee.get('manager_name', '')
        start_date = employee.get('effective_start_date', '')

        print(person_name)
        for journey in journeys:
            category = journey['category']

            # Assign the appropriate journey based on worker category
            if category == config.JRN_boarding_category['onboarding_category']:
                journey_response, status_code = assign_onboarding_journey_with_manager_and_hr(journey['name'], person_name)
            else:
                continue

            # Fetch the list of tasks assigned to the employee
           
            assigned_tasks = journey_response.get('assigned_tasks', {})

  
            task_list_html = "".join(f"<li>{task['task_name']} (Due: {task['task_due_date']})</li>" for task in assigned_tasks)
            action_name = person_name
            # for task in assigned_tasks:
            #     action_name = task['action_name']

            # # Prepare the email data
            # print(action_name)
            email_data = {
                "to_email": employee_email,
                "from_email": config.SMTP_CONFIG['from_email'],
                "template_name": config['templates']['onboarding_journey_assigned_today'],
                "data": {
                    "person_name": person_name,
                    "company_name": config.others['company_name'],
                    "journey_name": journey['name'],
                    "start_date": start_date,
                    "task_list": task_list_html,
                    "manager_name": manager_name,
                    "action_name":person_name
                }
            }

            # Send the onboarding email
            send_email(email_data)

    return {"message": "Journeys assigned for all employees starting today"}, 200
def assign_offboarding_journeys_for_today():
    db = get_database()
    employee_collection = db[config.HRM_employee_details]
    today = datetime.now().strftime('%Y-%m-%d')
    # Find unique employees with today's start date
    employees = list(employee_collection.aggregate([
        {'$match': {'effective_end_date': today}},
        {'$group': {'_id': '$person_name', 'employee_data': {'$first': '$$ROOT'}}}
    ]))
   
    if not employees:
        return {"message": "No employees found with today's start date"}, 200

    journey_collection = db[config.JRN_journey]
    journeys = list(journey_collection.find({}, {'name': 1, 'category': 1, '_id': 0}))

    # Iterate through unique employees
    for employee_entry in employees:
        employee = employee_entry['employee_data']
        person_name = employee["person_name"]
        employment_type = employee["employment_type"].lower()
        grade = employee.get('grade', '')
        employee_email = employee.get('email', '')
        manager_name = employee.get('manager_name', '')
        start_date = employee.get('effective_start_date', '')

        print(person_name)
        for journey in journeys:
            category = journey['category']

            # Assign the appropriate journey based on worker category
            if category == config.JRN_boarding_category['offboarding_cateogry']:
                journey_response, status_code = assign_onboarding_journey_with_manager_and_hr(journey['name'], person_name)
            else:
                continue


            # Fetch the list of tasks assigned to the employee
           
            assigned_tasks = journey_response.get('assigned_tasks', {})

  
            task_list_html = "".join(f"<li>{task['task_name']} (Due: {task['task_due_date']})</li>" for task in assigned_tasks)



            # Prepare the email data
           
            last_working_day = datetime.now().strftime('%Y-%m-%d')  # Replace with the actual last working day
            exit_interview_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')  # Example exit interview date

            email_data = {
                "to_email": employee_email,
                "from_email": config.SMTP_CONFIG['from_email'],
                "template_name": config['templates']['employee_offboarding'],
                "data": {
                    "person_name": person_name,
                    "company_name": config.others['company_name'],
                    "last_working_day": last_working_day,
                    "exit_interview_date": exit_interview_date,
                    "task_list": task_list_html,
                    "manager_name": manager_name,
                    "action_name":person_name
                }
            }

            # Send the onboarding email
            send_email(email_data)

    return {"message": "Journeys Offbaording assigned for all employees ending today"}, 200



def assign_onboarding_journey_with_manager_and_hr(journey_title, person_name):
    db = get_database()
    journey_collection = db[config.JRN_journey]
    task_collection = db[config.JRN_task]
    employee_collection = db[config.HRM_employee_details]
    print(journey_title+person_name)
 

    try:
        # Find the journey
        journey = journey_collection.find_one({'name': journey_title})
        if not journey:
            return {'error': 'Journey not found'}, 404

        # Retrieve employee details, including manager and HR
        employee = employee_collection.find_one({'person_name': person_name})
        if not employee:
            return {'error': 'Employee not found'}, 404
      
        if  not check_employee_eligibility_for_JRN(person_name, journey_title):
            return {'error': f'Employee {person_name} is not eligible for journey {journey_title}'}, 403
       
        # Get manager_name and hr_name from the employee record
        manager_name = employee.get("manager_name", None)
        hr_name = hr_name_fetch(employee)
        print(manager_name)
        print(hr_name)


        # Initialize task arrays for employee, manager, and HR
        employee_tasks = []
        manager_tasks = []
        hr_tasks = []
        assigned_tasks=[]

        # Assign tasks based on performer
        for task_name in journey['tasks']:
            task_info = task_collection.find_one({'task_name': task_name})
            if not task_info:
                # continue
                return {'error': f'Task {task_name} not found in task collection'}, 404
    
            task_due_date = datetime.now() + timedelta(days=task_info['duration'])

           


            # If an eligibility profile exists, check task eligibility for the employee
            if not check_employee_eligibility_for_task(person_name, task_name):
                print(f"Employee {person_name} is not eligible for task {task_name}")
                continue  # Skip the task if the employee is not eligible
            print(person_name+"eligible for "+task_name)
             # Assign tasks to the employee
            if task_info.get('performer').lower() == "employee":

                employee_tasks.append({
                    "task_name": task_name,
                    "status": "Not Started",
                    "task_start_date": datetime.now().strftime('%Y-%m-%d'),
                    "task_due_date": task_due_date.strftime('%Y-%m-%d'),
                    "time_status": "On time",
                    "feedback": "",
                    "performer": "employee",
                    "action_name": person_name  # Use person_name as action_name
                })
                assigned_tasks.append({"task_name": task_name, "task_due_date": task_due_date.strftime('%Y-%m-%d')})


            # Assign tasks to the manager
            if manager_name and task_info.get('performer').lower() == "manager":
                manager_tasks.append({
                    "task_name": task_name,
                    "status": "Not Started",
                    "task_start_date": datetime.now().strftime('%Y-%m-%d'),
                    "task_due_date": task_due_date.strftime('%Y-%m-%d'),
                    "time_status": "On time",
                    "feedback": "",
                    "performer": "manager",
                    "action_name": person_name  # Use person_name as action_name
                })

            # Assign tasks to the HR representative
            if hr_name and task_info.get('performer').lower() == "hr":
                hr_tasks.append({
                    "task_name": task_name,
                    "status": "Not Started",
                    "task_start_date": datetime.now().strftime('%Y-%m-%d'),
                    "task_due_date": task_due_date.strftime('%Y-%m-%d'),
                    "time_status": "On time",
                    "feedback": "",
                    "performer": "HR",
                    "action_name": person_name  # Use person_name as action_name
                })
            
        
        print("for loop ended")
        
        result = journey_collection.update_one(
            {'name': journey_title},
            {'$addToSet': {'users': {
                'person_name': person_name,
                'status': 'In Progress',
                'tasks': employee_tasks  # Employee tasks
            }}}
        )
        print("added in jounrey "+journey_title)

        # if result.modified_count == 0:
        #     return {'error': 'Failed to assign onboarding journey'}, 500

        # Add manager tasks if manager_name is valid
        if manager_name:
            assign_tasks_to_person(journey_title, manager_name, manager_tasks,person_name)

        # Add HR tasks if hr_name is valid
        if hr_name:
            assign_tasks_to_person(journey_title, hr_name, hr_tasks,person_name)

        return {"message": f"Onboarding journey assigned to {person_name}, manager, and HR (if applicable)", "assigned_tasks": assigned_tasks}, 200

    except Exception as e:
        return {'error': str(e)}, 500


def assign_tasks_to_person(journey_title, person_name, tasks,action_name):
    db = get_database()
    journey_collection = db[config.JRN_journey]
    employee_collection = db[config.HRM_employee_details]

    try:
        # Add tasks for the person (manager or HR)
        result = journey_collection.update_one(
            {'name': journey_title},
            {'$addToSet': {'users': {
                'person_name': person_name,
                'status': 'In Progress',
                'tasks': tasks
            }}}
        )

        if result.modified_count == 0:
            return {'error': 'Failed to assign tasks'}, 500
          # Retrieve the person's email
        person = employee_collection.find_one({'person_name': person_name})
        if not person:
            return {'error': f'{person_name} not found in employee collection'}, 404

        person_email = person.get('email', '')

        # Prepare the task list for the email
        task_list_html = "".join(f"<li>{task['task_name']} - Due by {task['task_due_date']}</li>" for task in tasks)
        print(person_email)
        # Prepare email data
        email_data = {
            "to_email": person_email,
            "from_email": config.SMTP_CONFIG['from_email'],
            "template_name": config['templates']['tasks_assigned'],  # Ensure this template exists in your email template collection
            "data": {
                "person_name": person_name,
                "company_name": config.others['company_name'],  # Replace with your company name
                "journey_name": journey_title,
                "task_list": task_list_html,
                "action_name":action_name
            }
        }

        # Send the email notification
        
      
        send_email(email_data)

        return {"message": f"Tasks assigned to {person_name}"}, 200

    except Exception as e:
        return {'error': str(e)}, 500


def remove_employee_and_cleanup_journeys(person_name):
    db = get_database()
    employee_collection = db[config.HRM_employee_details]
    journey_collection = db[config.JRN_journey]
    
    try:
        # Step 1: Check if the employee exists in the employee collection
        employee = employee_collection.find_one({'person_name': person_name})
        if not employee:
            return {"error": f"Employee {person_name} not found in the employee collection"}, 404

        # Step 2: Unassign the employee from all journeys and teams
        journeys = journey_collection.find({
            '$or': [
                {'users.person_name': person_name},
                {'teams.teammembers.person_name': person_name}
            ]
        })
        if journeys:
            for journey in journeys:
                journey_name = journey['name']
                response, status_code = unassign_journey_from_user(journey_name, person_name)
                response, status_code = unassign_journey_from_user_for_team(journey_name,person_name)
                if status_code != 200:
                    return {"error": f"Failed to unassign journey {journey_name} for employee {person_name}: {response.get('error')}"}, 500

        # Step 3: Remove the employee from the employee collection
        # result = employee_collection.delete_one({'person_name': person_name})
        # if result.deleted_count == 0:
        #     return {"error": f"Failed to remove employee {person_name} from the employee collection"}, 500
        
        return {"message": f"Employee {person_name} removed successfully and unassigned from all journeys and teams"}, 200
    
    except Exception as e:
        return {"error": str(e)}, 500


def remove_task_and_cleanup_user_for_team(journey_title, person_name, team_member_name):
    db = get_database()
    journey_collection = db[config.JRN_journey]
    try:
        # Step 1: Remove the task that matches the action_name from the team member's tasks
        result = journey_collection.update_one(
            {
                'name': journey_title,
                'teams.teammembers': {
                    '$elemMatch': {
                        'person_name': team_member_name,
                        'tasks.action_name': person_name  # Use action_name instead of task_name + person_name
                    }
                }
            },
            {
                '$pull': {
                    'teams.$[].teammembers.$[tm].tasks': {
                        'action_name': person_name  # Use action_name
                    }
                }
            },
            array_filters=[{'tm.person_name': team_member_name}]
        )

        if result.modified_count > 0:
            print(f"Task related to {person_name} removed from {team_member_name}'s tasks.")

            # Step 2: Check if the specific team member's task list is now empty
            user_with_empty_tasks = journey_collection.find_one(
                {
                    'name': journey_title,
                    'teams.teammembers': {
                        '$elemMatch': {
                            'person_name': team_member_name,
                            'tasks': {'$size': 0}
                        }
                    }
                }
            )

            if user_with_empty_tasks:
                # Step 3: If no tasks left, remove this specific user object from the team members array
                delete_result = journey_collection.update_one(
                    {
                        'name': journey_title,
                        'teams.teammembers.person_name': team_member_name,
                        'teams.teammembers.tasks': {'$size': 0}
                    },
                    {
                        '$pull': {
                            'teams.$[].teammembers': {'person_name': team_member_name, 'tasks': {'$size': 0}}
                        }
                    }
                )

                if delete_result.modified_count > 0:
                    print(f"{team_member_name} has been removed from the journey because they have no tasks left.")
                    return {"message": f"{team_member_name} removed from journey as they have no tasks left"}, 200

            return {"message": f"Task related to {person_name} removed from {team_member_name}'s tasks"}, 200
        else:
            print(f"No tasks removed for {team_member_name}.")
            return {"message": f"No tasks removed for {team_member_name}"}, 400

    except Exception as e:
        print("Error:", str(e))
        return {"error": str(e)}, 500


# Example usage:
# remove_task_and_cleanup_user("Badge Request", "Vishal Meena", "Nikhil")



def unassign_journey_from_user_for_team(journey_title, person_name):
    db = get_database()
    journey_collection = db[config.JRN_journey]
    employee_collection = db[config.HRM_employee_details]

    try:
        # Find the journey and check if the user is assigned to any team within the journey
        journey = journey_collection.find_one({
            'name': journey_title,
            'teams.teammembers.person_name': person_name
        })

        if not journey:
            return {'error': f'User {person_name} not found in journey {journey_title}'}, 200

        # Remove the user from the journey's team members
        result = journey_collection.update_one(
            {'name': journey_title},
            {'$pull': {'teams.$[].teammembers': {'person_name': person_name}}}
        )

        if result.modified_count == 0:
            return {'error': 'Failed to unassign the user from the journey'}, 500

        # Get employee email, manager name, and HR name
        employee = employee_collection.find_one({'person_name': person_name})
        if employee:
            employee_email = employee.get('email', '')
            manager_name = employee.get('manager_name', '')
            hr_name = hr_name_fetch(employee)

            # Remove and clean up related tasks for the manager and HR
            if manager_name:
                remove_task_and_cleanup_user_for_team(journey_title, person_name, manager_name)
            if hr_name:
                remove_task_and_cleanup_user_for_team(journey_title, person_name, hr_name)

            # Prepare and send notification email to the user
            if employee_email:
                email_data = {
                    "to_email": employee_email,
                    "from_email": config.SMTP_CONFIG['from_email'],
                    "template_name": config['templates']['user_unassigned_from_journey'],
                    "data": {
                        "person_name": person_name,
                        "company_name": config.others['company_name'],
                        "journey_name": journey_title,
                        "manager_name": manager_name,
                        "action_name":person_name
                    }
                }
                send_email(email_data)

            # Send notification email to the manager
            if manager_name:
                manager = employee_collection.find_one({'person_name': manager_name})
                if manager and manager.get('email', ''):
                    manager_email_data = {
                        "to_email": manager['email'],
                        "from_email": config.SMTP_CONFIG['from_email'],
                        "template_name": config['templates']['user_unassigned_from_journey'],
                        "data": {
                            "person_name": manager_name,
                            "company_name": config.others['company_name'],
                            "journey_name": journey_title,
                            "manager_name": manager_name,
                            "action_name":person_name
                        }
                    }
                    send_email(manager_email_data)

            # Send notification email to HR
            if hr_name:
                hr = employee_collection.find_one({'person_name': hr_name})
                if hr and hr.get('email', ''):
                    hr_email_data = {
                        "to_email": hr['email'],
                        "from_email": config.SMTP_CONFIG['from_email'],
                        "template_name": config['templates']['user_unassigned_from_journey'],
                        "data": {
                            "person_name": hr_name,
                            "company_name": config.others['company_name'],
                            "journey_name": journey_title,
                            "manager_name": manager_name,
                            "action_name":person_name
                        }
                    }
                    send_email(hr_email_data)

        return {'message': f'User {person_name} successfully unassigned from journey {journey_title} and related tasks removed for manager and HR'}, 200

    except Exception as e:
        return {'error': str(e)}, 500




def add_user_to_journey(journey_title, user):
    db = get_database()
    employee_collection = db[config.HRM_employee_details]
    journey_collection = db[config.JRN_journey]

    try:
        # Retrieve employee details
        employee = employee_collection.find_one({'person_name': user['person_name']})
        if not employee:
            return {'error': 'Employee not found'}, 404

        # Call the function to assign the onboarding journey to the user, their manager, and HR
                # Check if the user is already added to the journey
        # action_name = user['person_name']

        # Check if the user with the same action_name is already added to the journey
        journey = journey_collection.find_one({
            'name': journey_title,
            'users': {
                '$elemMatch': {
                    'person_name': user['person_name'],
                    'tasks.action_name': user['person_name']
                }
            }
        })
        if journey:
            return {'message': f'User is already added to this journey'}, 200

        journey_response, status_code = assign_onboarding_journey_with_manager_and_hr(journey_title, user['person_name'])

        if status_code != 200:
            return journey_response, status_code

        # Extract the assigned tasks from the response
        assigned_task_list = journey_response.get('assigned_tasks', {})

        # Prepare email data
        employee_email = employee.get('email', '')
        manager_name = employee.get('manager_name', '')
        company_name = config.others['company_name']

        # Prepare the task list for the email
        task_list_html = "".join(f"<li>{task['task_name']} (Due: {task['task_due_date']})</li>" for task in assigned_task_list)
        print("yes")
     
        if employee_email:
            # Send email notification to the employee
            email_data = {
                "to_email": employee_email,
                "from_email": config.SMTP_CONFIG['from_email'],
                "template_name": config['templates']['user_added_to_journey'],  # Ensure this template exists in your email template collection
                "data": {
                    "person_name": user['person_name'],
                    "company_name": company_name,
                    "journey_name": journey_title,
                    "start_date": datetime.now().strftime('%Y-%m-%d'),
                    "task_list": task_list_html,
                    "manager_name": manager_name,
                    "action_name": user['person_name']
                }
            }
            send_email(email_data)

        return {'message': 'User added successfully and onboarding journey assigned'}, 200
    except Exception as e:
        return {'error': str(e)}, 500


def add_user_to_journey2(journey_title, user):
    db = get_database()
    collection = db[config.JRN_journey]
    task_collection = db[config.JRN_task]
    employee_collection = db[config.HRM_employee_details]
    journey_collection = db[config.JRN_journey]
    try:
        journey = collection.find_one({'name': journey_title})
        if not journey:
            return {'error': 'Journey not found'}, 404

        employee = employee_collection.find_one({'person_name': user['person_name']})
        if not employee:
            return {'error': 'Employee not found'}, 404

        journey = journey_collection.find_one({
            'name': journey_title,
            'users': {
                '$elemMatch': {
                    'person_name': user['person_name'],
                    'tasks.action_name': user['person_name']
                }
            }
        })
        if journey:
            return {'message': f'User is already added to this journey'}, 200

        grade = employee.get('grade', '')
        employee_email = employee.get('email', '')
        manager_name = employee.get('manager_name', '')

        tasks = []
        assigned_task_list = []
        for task_name in journey['tasks']:
            task_info = task_collection.find_one({'task_name': task_name})
            if not task_info:
                return {'error': f'Task {task_name} not found in task collection'}, 404
            if task_info.get('performer').lower() == grade.lower():
                task_due_date = datetime.now() + timedelta(days=task_info['duration'])
                task_detail = {
                    "task_name": task_name,
                    "status": "In progress",
                    "task_start_date": datetime.now().strftime('%Y-%m-%d'),
                    "task_due_date": task_due_date.strftime('%Y-%m-%d'),
                    "time_status": "On time",
                    "feedback": "",
                    "performer": task_info.get('performer'),
                    "action_name": user['person_name']  # Use person_name as action_name
                }
                tasks.append(task_detail)
                assigned_task_list.append(f"<li>{task_name}</li>")

        user['tasks'] = tasks
        result = collection.update_one(
            {'name': journey_title},
            {'$addToSet': {'users': user}}
        )
        print(employee_email)
        if result.modified_count == 0:
            return {'error': 'User already added'}, 400

        # Send email notification
        email = {
            "to_email": employee_email,
            "from_email": config.SMTP_CONFIG['from_email'],
            "template_name": config['templates']['user_added_to_journey'],  # Ensure this template exists in your email template collection
            "data": {
                    "person_name": user['person_name'],
                    "company_name": config.others['company_name'],
                    "journey_name": journey_title,
                    "start_date": datetime.now().strftime('%Y-%m-%d'),
                    "task_list": "".join(assigned_task_list),
                    "manager_name": manager_name
            }
        }
        send_email(email)

        return {'message': 'User added successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500



def assign_task_to_user(journey_title, user,new_task_name):
    db = get_database()
    journey_collection = db[config.JRN_journey]
    task_collection = db[config.JRN_task]
    employee_collection = db[config.HRM_employee_details]
    try:
        # Fetch the task details
        task_info = task_collection.find_one({'task_name': new_task_name})
        if not task_info:
            return {'error': f'Task {new_task_name} not found in task collection'}, 404

        task_due_date = datetime.now() + timedelta(days=task_info['duration'])

        # Find a task in the user's tasks that matches the performer
        matching_task = next(
            (task for task in user.get('tasks', [])
             if task['performer'].lower() == task_info.get('performer').lower()), 
            None
        )

        if not matching_task:
            print("no matching performer")
            return {'message': f'No matching performer for {user["person_name"]}'}, 200

        # Create the new task based on the existing performer's action name
        new_task = {
            "task_name": new_task_name,
            "status": "Not Started",
            "task_start_date": datetime.now().strftime('%Y-%m-%d'),
            "task_due_date": task_due_date.strftime('%Y-%m-%d'),
            "time_status": "On time",
            "feedback": "",
            "performer": task_info.get('performer'),
            "action_name": matching_task['action_name']
        }

        # Assign the task to the user
        result = journey_collection.update_one(
            {
                'name': journey_title,
                'users': {
                    '$elemMatch': {
                        'person_name': user['person_name'],
                        'tasks': {
                            '$elemMatch': {
                                
                                'action_name': new_task['action_name']
                            }
                        }
                    }
                }
            },
            {'$addToSet': {'users.$.tasks': new_task}}
        )


        if result.modified_count == 0:
            return {'error': f'Failed to add task to {user["person_name"]}'}, 500

        # Notify the user via email
        employee = employee_collection.find_one({'person_name': user['person_name']})
        if employee and employee.get('email', ''):
            task_list_html = f"<li>{new_task_name} - Due by {new_task['task_due_date']}</li>"
            email_data = {
                "to_email": employee['email'],
                "from_email": config.SMTP_CONFIG['from_email'],
                "template_name": config['templates']['tasks_assigned'],
                "data": {
                    "person_name": user['person_name'],
                    "company_name": config.others['company_name'],
                    "journey_name": journey_title,
                    "task_list": task_list_html,
                    "action_name": new_task['action_name']
                }
            }
            send_email(email_data)
        return {'message': f'Task assigned to {user["person_name"]}'}, 200
   
    except Exception as e:
        return {'error': str(e)}, 500

def assign_task_to_team_member(journey_title, team_name, team_member,new_task_name):
    db = get_database()
    journey_collection = db[config.JRN_journey]
    task_collection = db[config.JRN_task]
    employee_collection = db[config.HRM_employee_details]
    print(team_name)

    try:
        # Fetch the task details
        task_info = task_collection.find_one({'task_name': new_task_name})
        if not task_info:
            return {'error': f'Task {new_task_name} not found in task collection'}, 404

        task_due_date = datetime.now() + timedelta(days=task_info['duration'])

        # Find a task in the team member's tasks that matches the performer
        matching_task = next(
            (task for task in team_member.get('tasks', [])
             if task['performer'].lower() == task_info.get('performer').lower()), 
            None
        )

        if not matching_task:
            return {'message': f'No matching performer for {team_member["person_name"]}'}, 200

        # Create the new task based on the existing performer's action name

        new_task = {
            "task_name": new_task_name,
            "status": "Not Started",
            "task_start_date": datetime.now().strftime('%Y-%m-%d'),
            "task_due_date": task_due_date.strftime('%Y-%m-%d'),
            "time_status": "On time",
            "feedback": "",
            "performer": task_info.get('performer'),
            "action_name": matching_task['action_name']
        }

        result = journey_collection.update_one(
            {
                'name': journey_title,
                'teams.team_name': team_name,
                'teams.teammembers': {
                    '$elemMatch': {
                        'person_name': team_member['person_name'],
                        'tasks': {
                            '$elemMatch': {
                                'performer': new_task['performer'],
                                'action_name': new_task['action_name']
                            }
                        }
                    }
                }
            },
            {'$addToSet': {'teams.$[team].teammembers.$[tm].tasks': new_task}},
            array_filters=[
                {'team.team_name': team_name},
                {'tm.person_name': team_member['person_name'], 'tm.tasks': {'$elemMatch': {'performer': new_task['performer']}}}
            ]
        )


        if result.modified_count == 0:
            return {'error': f'Failed to add task to {team_member["person_name"]}'}, 500

        # Notify the team member via email
        employee = employee_collection.find_one({'person_name': team_member['person_name']})
        if employee and employee.get('email', ''):
            task_list_html = f"<li>{new_task_name} - Due by {new_task['task_due_date']}</li>"
            email_data = {
                "to_email": employee['email'],
                "from_email": config.SMTP_CONFIG['from_email'],
                "template_name": config['templates']['tasks_assigned'],
                "data": {
                    "person_name": team_member['person_name'],
                    "company_name": config.others['company_name'],
                    "journey_name": journey_title,
                    "task_list": task_list_html,
                    "action_name": new_task['action_name']
                }
            }
            send_email(email_data)
        
        return {'message': f'Task assigned to {team_member["person_name"]}'}, 200

    except Exception as e:
        return {'error': str(e)}, 500

def remove_task_from_journey(journey_title, task_name_to_remove):
    db = get_database()
    journey_collection = db[config.JRN_journey]
    task_collection = db[config.JRN_task]
    employee_collection = db[config.HRM_employee_details]

    try:
        # Step 1: Fetch the journey details
        journey = journey_collection.find_one({'name': journey_title})
        if not journey:
            return {'error': 'Journey not found'}, 404

        # Step 2: Remove the task from the journey's task list
        if task_name_to_remove in journey.get('tasks', []):
            journey_collection.update_one(
                {'name': journey_title},
                {'$pull': {'tasks': task_name_to_remove}}
            )

        # Step 3: Remove the task from individual users' task lists
        for user in journey.get('users', []):
            result = journey_collection.update_one(
                {
                    'name': journey_title,
                    'users.person_name': user['person_name']
                },
                {'$pull': {'users.$.tasks': {'task_name': task_name_to_remove}}}
            )
            if result.modified_count > 0:
                print(f"Task '{task_name_to_remove}' removed from {user['person_name']}'s task list.")

        # Step 4: Remove the task from each team member's task list
        for team in journey.get('teams', []):
            for team_member in team.get('teammembers', []):
                result = journey_collection.update_one(
                    {
                        'name': journey_title,
                        'teams.team_name': team['team_name'],
                        'teams.teammembers.person_name': team_member['person_name']
                    },
                    {'$pull': {'teams.$[team].teammembers.$[tm].tasks': {'task_name': task_name_to_remove}}},
                    array_filters=[
                        {'team.team_name': team['team_name']},
                        {'tm.person_name': team_member['person_name']}
                    ]
                )
                if result.modified_count > 0:
                    employee = employee_collection.find_one({'person_name': user['person_name']})
                    if employee and employee.get('email', ''):
                        email_data = {
                            "to_email": employee['email'],
                            "from_email": config.SMTP_CONFIG['from_email'],
                            "template_name": config['templates']['task_removal_from_jrn_notification'],
                            "data": {
                                "person_name": user['person_name'],
                                "removal_date": datetime.now().strftime('%Y-%m-%d'),
                                "journey_title": journey_title,
                                "task_name":task_name_to_remove
                            }
                        }
                        send_email(email_data)
                    print(f"Task '{task_name_to_remove}' removed from {team_member['person_name']}'s task list in team {team['team_name']}.")

        return {'message': f"Task '{task_name_to_remove}' removed from journey, users, and team members successfully."}, 200

    except Exception as e:
        return {'error': str(e)}, 500



def add_task_to_existing_users_and_teams(journey_title, new_task_name):
    db = get_database()
    journey_collection = db[config.JRN_journey]

    try:
        # Fetch the journey details
        journey = journey_collection.find_one({'name': journey_title})
        if not journey:
            return {'error': 'Journey not found'}, 404

        # Add the task to the journey's task list if it's not already there
        if new_task_name not in journey.get('tasks', []):
            journey_collection.update_one(
                {'name': journey_title},
                {'$addToSet': {'tasks': new_task_name}}
            )

        # Assign the task to individual users
        for user in journey.get('users', []):
            if not check_employee_eligibility_for_task(user['person_name'], new_task_name):
                print(f"User {user['person_name']} is not eligible for task {new_task_name}")
                continue  # Skip the user if not eligible
            
            assign_task_to_user(journey_title, user,new_task_name)
        # Assign the task to each team member
        for team in journey.get('teams', []):
            for team_member in team.get('teammembers', []):   
                if not check_employee_eligibility_for_task(team_member['person_name'], new_task_name):
                    print(f"Team member {team_member['person_name']} is not eligible for task {new_task_name}")
                    continue  # Skip the team member if not eligible               
                assign_task_to_team_member(journey_title, team['team_name'], team_member,new_task_name)

        return {'message': 'New task added to all applicable users and team members, with emails sent'}, 200

    except Exception as e:
        return {'error': str(e)}, 500




def send_overdue_task_notifications():
    db = get_database()
    journey_collection = db[config.JRN_journey]
    employee_collection = db[config.HRM_employee_details]
    try:
        # Get the current date
        current_date = datetime.now().date()

        # Fetch all journeys from the collection
        journeys = journey_collection.find()

        for journey in journeys:
            # Iterate through all users in the journey
            for user in journey.get('users', []):
                overdue_tasks = []
                for task in user.get('tasks', []):
                    if task['status'] != 'Completed':
                        due_date = datetime.strptime(task['task_due_date'], '%Y-%m-%d').date()
                        if current_date > due_date:
                            days_overdue = (current_date - due_date).days
                            overdue_tasks.append({
                                'task_name': task['task_name'],
                                'due_date': due_date.strftime('%Y-%m-%d'),
                                'days_overdue': days_overdue
                            })

                # Send email if there are overdue tasks
                employee = employee_collection.find_one({'person_name': user['person_name']})
                if overdue_tasks:
                    send_overdue_email(user['person_name'], employee.get('email', ''), overdue_tasks, journey.get('name', ''))

            # Iterate through all team members in the journey
            for team in journey.get('teams', []):
                for member in team.get('teammembers', []):
                    overdue_tasks = []
                    for task in member.get('tasks', []):
                        if task['status'] != 'Completed':
                            due_date = datetime.strptime(task['task_due_date'], '%Y-%m-%d').date()
                            if current_date > due_date:
                                days_overdue = (current_date - due_date).days
                                overdue_tasks.append({
                                    'task_name': task['task_name'],
                                    'due_date': due_date.strftime('%Y-%m-%d'),
                                    'days_overdue': days_overdue
                                })

                    # Send email if there are overdue tasks
                    employee = employee_collection.find_one({'person_name': member['person_name']})
                    if overdue_tasks:
                        send_overdue_email(member['person_name'], employee.get('email', ''), overdue_tasks, journey.get('name', ''))

        return {"message": "Overdue task notifications sent"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def send_overdue_email(person_name, email, overdue_tasks, journey_name):
    if not email:
        print(f"No email found for {person_name}. Skipping notification.")
        return
    print(person_name+email)
   

    task_list_html = "".join(
        f"<li>{task['task_name']} - Due by {task['due_date']} - Overdue by {task['days_overdue']} days</li>"
        for task in overdue_tasks
    )
   
    email_data = {
        "to_email": email,
        "from_email": config.SMTP_CONFIG['from_email'],
        "template_name": "tasks_overdue2",  # Ensure this template exists
        "data": {
            "person_name": person_name,
            "journey_name": journey_name,
            "company_name": config.others['company_name'],
            "task_list": task_list_html,
            "current_year": datetime.now().year
        }
    }
    print("yes")
    send_email(email_data)
    print(f"Overdue task email sent to {person_name} at {email}")

