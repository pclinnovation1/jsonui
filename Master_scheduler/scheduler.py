import schedule
import time
import threading
import json
import sys
import os
from functools import partial
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database setup
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
db = client['PCL_Interns']
process_details_collection = db['Process_Details']

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

# Schedule tasks based on configuration
def schedule_tasks(config):
    for task in config['tasks']:
        task_func = TASKS[task['name']]
        params = get_env_parameters(task['name'])

        # Create process details document in the database
        process_details_id = process_details_collection.insert_one({
            "Process ID": str(ObjectId()),
            "Name": task['name'],
            "Metadata Name": task['name'],
            "Status": "Scheduled",
            "Submitted By": "scheduler_user",
            "Submission Notes": "Scheduled task",
            "Start Time": "",
            "Scheduled Time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "Submission Time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "Completion Time": "",
            "All Parameters": {f"Argument{i+1}": param for i, param in enumerate(params)}
        }).inserted_id

        # Use partial to include process_details_id and db
        task_func_with_params = partial(task_func, *params, process_details_id=process_details_id, db=db)

        if task['interval'] == 'every':
            interval, unit = task['time'].split()
            interval = int(interval)

            if unit == 'seconds':
                schedule.every(interval).seconds.do(task_func_with_params)
            elif unit == 'minutes':
                schedule.every(interval).minutes.do(task_func_with_params)
            elif unit == 'hours':
                schedule.every(interval).hours.do(task_func_with_params)
            elif unit == 'day':
                schedule.every().day.at(task['at']).do(task_func_with_params)

# Run the task and update parameters
def run_task(task_func, *params, process_details_id, db):
    process_details_collection = db['Process_Details']
    
    process_details_collection.update_one(
        {'_id': process_details_id},
        {'$set': {'Start Time': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'Status': 'Running'}}
    )
    task_func(*params, process_details_id, db)  # Execute the task with the latest parameters
    process_details_collection.update_one(
        {'_id': process_details_id},
        {'$set': {'Completion Time': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'Status': 'Completed'}}
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
