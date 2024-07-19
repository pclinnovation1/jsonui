import schedule
import time
import threading
import json
import sys
import os
from functools import partial
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

# Load environment variables from .env file
load_dotenv()

# Database setup
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
db = client['PCL_Interns']
process_details_collection = db['S_Process_Details']

# Ensure an index on Completion Time in descending order
process_details_collection.create_index([('Completion Time', DESCENDING)])

# Add tasks directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'tasks')))

# Import tasks from separate files
from generate_letters import generate_letters
from generate_notifications import generate_notifications
from assign_courses import assign_courses

# Map task names to functions
TASKS = {
    'generate_letters': generate_letters,
    'generate_notifications': generate_notifications,
    'assign_courses': assign_courses
}

# Load configuration from JSON file
def load_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)

# Get parameters from the environment variables
def get_env_parameters(task_name):
    params = []
    for key in os.environ:
        if key.startswith(task_name.upper()):
            params.append(os.getenv(key))
    return params

# Get next scheduled time for the task
def get_next_scheduled_time(interval, unit):
    now = datetime.now(timezone.utc)
    if unit == 'second':
        return now + timedelta(seconds=interval)
    elif unit == 'minute':
        return now + timedelta(minutes=interval)
    elif unit == 'hour':
        return now + timedelta(hours=interval)
    elif unit == 'day':
        return now + timedelta(days=interval)
    else:
        return now

# Schedule tasks based on configuration
def schedule_tasks(config):
    for task in config['tasks']:
        task_func = TASKS[task['name']]
        params = get_env_parameters(task['name'])

        interval, unit = task['time'].split()
        interval = int(interval)
        unit = unit.lower()
        if unit.endswith('s'):
            unit = unit[:-1]  # Remove the trailing 's'

        # Attachment file path from environment variable
        attachment_file = os.getenv(f"{task['name'].upper()}_ATTACHMENT", "")

        # Use partial to include parameters needed for the task
        task_func_with_params = partial(run_task, task_func, *params, task_name=task['name'], interval=interval, unit=unit, attachment_file=attachment_file)

        if task['interval'] == 'every':
            if unit == 'second':
                schedule.every(interval).seconds.do(run_in_thread, task_func_with_params)
            elif unit == 'minute':
                schedule.every(interval).minutes.do(run_in_thread, task_func_with_params)
            elif unit == 'hour':
                schedule.every(interval).hours.do(run_in_thread, task_func_with_params)
            elif unit == 'day':
                schedule.every(interval).days.do(run_in_thread, task_func_with_params)

# Run the task in a separate thread
def run_in_thread(task_func_with_params):
    task_thread = threading.Thread(target=task_func_with_params)
    task_thread.start()

# Run the task and create a new entry for each cycle
def run_task(task_func, *params, task_name, interval, unit, attachment_file):
    process_details_collection = db['S_Process_Details']

    # Generate a new process_details_id for each run
    process_details_id = ObjectId()
    start_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    next_scheduled_time = get_next_scheduled_time(interval, unit).strftime('%Y-%m-%dT%H:%M:%SZ')

    # Create a new process details document for this run
    process_details_collection.insert_one({
        "_id": process_details_id,
        "Name": task_name,
        "Metadata Name": task_name,
        "Status": "Running",
        "Submitted By": "scheduler_user",
        "Submission Notes": "Scheduled task",
        "Start Time": start_time,
        "Scheduled Time": start_time,
        "Next Scheduled Time": next_scheduled_time,
        "Submission Time": start_time,
        "Completion Time": "",
        "Attachment File": attachment_file,
        "All Parameters": {f"Argument{i+1}": param for i, param in enumerate(params)}
    })

    # Execute the task with the latest parameters
    task_start_time = datetime.now(timezone.utc)
    try:
        task_func(*params, process_details_id=process_details_id, db=db)
        status = 'Completed'
    except Exception as e:
        status = 'Failed'
        print(f"Error running task {task_name}: {e}")

    # Update the completion time and status
    completion_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    process_details_collection.update_one(
        {'_id': process_details_id},
        {'$set': {
            'Completion Time': completion_time, 
            'Status': status
        }}
    )

# Run the scheduler
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)  # Check for pending tasks every second

# Main function to start the scheduler in a separate thread
if __name__ == "__main__":
    # Load config
    config = load_config('config.json')

    # Schedule tasks
    schedule_tasks(config)

    # Run the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()

    # Keep the main thread alive
    while True:
        time.sleep(1)
