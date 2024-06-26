import schedule
import time
import threading
import json
import sys
import os
import logging
from functools import partial
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from fpdf import FPDF
import gridfs

# Load environment variables from .env file
load_dotenv()

# Database setup
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
db = client['PCL_Interns']
process_details_collection = db['Results_temp']
client_collection = db['Client_Collection']
processes_collection = db['Processes_Collection']
fs = gridfs.GridFS(db)

# Ensure an index on Completion Time in descending order
process_details_collection.create_index([('Completion Time', DESCENDING)])

# Add tasks directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'tasks')))

# Import tasks from separate files
from update_accrual_plan_enrollments import update_accrual_plan_enrollments
from evaluate_certification_updates import evaluate_certification_updates
from calculate_accruals_and_balances import calculate_accruals_and_balances

# Map task names to functions
TASKS = {
    'Calculate Accruals and Balances': calculate_accruals_and_balances,
    'Evaluate Certification Updates': evaluate_certification_updates,
    'Update Accrual Plan Enrollments': update_accrual_plan_enrollments
}

# Load configuration from database
def load_config_from_db():
    return list(client_collection.find())

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
    elif unit == 'week':
        return now + timedelta(weeks=interval)
    elif unit == 'month':
        return now + relativedelta(months=interval)
    elif unit == 'year':
        return now + relativedelta(years=interval)
    else:
        return now

# Setup logging
def setup_logging(process_name):
    log_filename = f"{process_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_filepath = os.path.join('logs', log_filename)
    
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger(process_name)
    logger.setLevel(logging.DEBUG)

    # File handler
    file_handler = logging.FileHandler(log_filepath)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%a %b %d %H:%M:%S UTC %Y')
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return log_filepath, logger

# Convert log file to PDF
def convert_log_to_pdf(log_filepath):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    with open(log_filepath, 'r') as file:
        for line in file:
            pdf.cell(200, 10, txt=line, ln=True)
    
    pdf_filepath = log_filepath.replace('.log', '.pdf')
    pdf.output(pdf_filepath)
    return pdf_filepath

# Read log file
def read_log_file(log_filepath):
    with open(log_filepath, 'r') as file:
        return file.read()

# Run the task and create a new entry for each cycle
def run_task(task_func, *params, task_name, interval, unit, attachment_file, process_id):
    process_details_collection = db['Results_temp']

    # Fetch all parameters from Client_Collection
    client_data = client_collection.find_one({'Process ID': process_id})
    all_parameters = client_data if client_data else {}

    # Generate a new process_details_id for each run
    process_details_id = ObjectId()
    start_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    next_scheduled_time = get_next_scheduled_time(interval, unit).strftime('%Y-%m-%dT%H:%M:%SZ')

    # Setup logging
    log_filepath, logger = setup_logging(task_name)
    
    # Create a new process details document for this run
    process_details_collection.insert_one({
        "Process ID": process_id,
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
        "Attachment File": "",
        "All Parameters": all_parameters,
    })

    # Execute the task with the latest parameters
    task_start_time = datetime.now(timezone.utc)
    try:
        logger.info(f"Executing {task_name} with parameters {params}")
        task_func(*params, process_details_id=process_details_id, db=db, attachment_file=log_filepath, logger=logger)
        status = 'Completed'
        logger.info(f"Process {task_name} completed successfully.")
    except Exception as e:
        status = 'Failed'
        logger.error(f"Error running task {task_name}: {e}")

    # Convert log to PDF and save it
    pdf_filepath = convert_log_to_pdf(log_filepath)
    with open(pdf_filepath, 'rb') as pdf_file:
        pdf_id = fs.put(pdf_file, filename=os.path.basename(pdf_filepath))

    process_details_collection.update_one(
        {'Process ID': process_id},
        {'$set': {
            'Completion Time': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 
            'Status': status,
            'Attachment File': pdf_id
        }}
    )

    # Update the final document in Processes_Collection
    final_document = {
        "Process ID": process_id,
        "Name": task_name,
        "Metadata Name": task_name,
        "Status": status,
        "Submitted By": "scheduler_user",
        "Submission Notes": "Scheduled task",
        "Start Time": start_time,
        "Scheduled Time": start_time,
        "Next Scheduled Time": next_scheduled_time,
        "Submission Time": start_time,
        "Completion Time": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        "Attachment File": pdf_id,
        "All Parameters": all_parameters,
        "Log Details": read_log_file(log_filepath)
    }
    process_details_collection.insert_one(final_document)

def schedule_task_with_end_check(task_func_with_params, end_date):
    if datetime.now(timezone.utc) <= end_date:
        run_in_thread(task_func_with_params)

# Run the task in a separate thread
def run_in_thread(task_func_with_params):
    task_thread = threading.Thread(target=task_func_with_params)
    task_thread.start()

# Schedule tasks based on configuration from database
def schedule_tasks_from_db(configs):
    for config in configs:
        task_func = TASKS.get(config['Process Name'])
        if not task_func:
            logging.warning(f"No task function found for '{config['Process Name']}'. Skipping.")
            continue
        
        params = []  # Collect any specific parameters needed
        schedule_data = config['AdvancedOptions']['Schedule']

        process_id = config.get('Process ID', str(ObjectId()))

        if 'AsSoonAsPossible' in schedule_data:
            run_in_thread(partial(run_task, task_func, *params, task_name=config['Process Name'], interval=0, unit='second', attachment_file="", process_id=process_id))
        elif 'UsingASchedule' in schedule_data:
            frequency = schedule_data['UsingASchedule']['Frequency']
            for freq_type, freq_details in frequency.items():
                if freq_type == 'Once':
                    start_date = datetime.fromisoformat(freq_details['Start Date']).replace(tzinfo=timezone.utc)
                    if datetime.now(timezone.utc) <= start_date:
                        schedule.once().at(start_date).do(run_in_thread, partial(run_task, task_func, *params, task_name=config['Process Name'], interval=0, unit='second', attachment_file="", process_id=process_id))
                elif freq_type == 'Hourly/Minute':
                    start_date = datetime.fromisoformat(freq_details['Start Date']).replace(tzinfo=timezone.utc)
                    end_date = datetime.fromisoformat(freq_details['End Date']).replace(tzinfo=timezone.utc)
                    interval = int(freq_details['Time Between Runs'].split()[0])
                    unit = freq_details['Time Between Runs'].split()[1].lower()
                    if unit == 'minute':
                        schedule.every(interval).minutes.do(schedule_task_with_end_check, partial(run_task, task_func, *params, task_name=config['Process Name'], interval=interval, unit='minute', attachment_file="", process_id=process_id), end_date=end_date)
                    elif unit == 'hour':
                        schedule.every(interval).hours.do(schedule_task_with_end_check, partial(run_task, task_func, *params, task_name=config['Process Name'], interval=interval, unit='hour', attachment_file="", process_id=process_id), end_date=end_date)
                elif freq_type == 'Daily':
                    start_date = datetime.fromisoformat(freq_details['Start Date']).replace(tzinfo=timezone.utc)
                    end_date = datetime.fromisoformat(freq_details['End Date']).replace(tzinfo=timezone.utc)
                    interval = int(freq_details['Days Between Runs'])
                    schedule.every(interval).days.do(schedule_task_with_end_check, partial(run_task, task_func, *params, task_name=config['Process Name'], interval=interval, unit='day', attachment_file="", process_id=process_id), end_date=end_date)
                elif freq_type == 'Weekly':
                    start_date = datetime.fromisoformat(freq_details['Start Date']).replace(tzinfo=timezone.utc)
                    end_date = datetime.fromisoformat(freq_details['End Date']).replace(tzinfo=timezone.utc)
                    interval = int(freq_details['Weeks Between Runs'])
                    schedule.every(interval).weeks.do(schedule_task_with_end_check, partial(run_task, task_func, *params, task_name=config['Process Name'], interval=interval, unit='week', attachment_file="", process_id=process_id), end_date=end_date)
                elif freq_type == 'Monthly':
                    start_date = datetime.fromisoformat(freq_details['Start Date']).replace(tzinfo=timezone.utc)
                    end_date = datetime.fromisoformat(freq_details['End Date']).replace(tzinfo=timezone.utc)
                    if 'Repeat By day' in freq_details:
                        week_of_month = freq_details['Repeat By day']['Week of the Month']
                        day_of_week = freq_details['Repeat By day']['Day of the Week']
                        schedule.every().month.at(f'{week_of_month} {day_of_week}').do(schedule_task_with_end_check, partial(run_task, task_func, *params, task_name=config['Process Name'], interval=1, unit='month', attachment_file="", process_id=process_id), end_date=end_date)
                    elif 'Repeat By date' in freq_details:
                        date = int(freq_details['Repeat By date']['Date'])
                        schedule.every().month.at(f'{date}').do(schedule_task_with_end_check, partial(run_task, task_func, *params, task_name=config['Process Name'], interval=1, unit='month', attachment_file="", process_id=process_id), end_date=end_date)
                elif freq_type == 'Yearly':
                    start_date = datetime.fromisoformat(freq_details['Start Date']).replace(tzinfo=timezone.utc)
                    end_date = datetime.fromisoformat(freq_details['End Date']).replace(tzinfo=timezone.utc)
                    month = int(freq_details['Month'])
                    if 'Repeat By day' in freq_details:
                        week_of_month = freq_details['Repeat By day']['Week of the Month']
                        day_of_week = freq_details['Repeat By day']['Day of the Week']
                        schedule.every().year.at(f'{month} {week_of_month} {day_of_week}').do(schedule_task_with_end_check, partial(run_task, task_func, *params, task_name=config['Process Name'], interval=1, unit='year', attachment_file="", process_id=process_id), end_date=end_date)
                    elif 'Repeat By date' in freq_details:
                        date = int(freq_details['Repeat By date']['Date'])
                        schedule.every().year.at(f'{month}-{date}').do(schedule_task_with_end_check, partial(run_task, task_func, *params, task_name=config['Process Name'], interval=1, unit='year', attachment_file="", process_id=process_id), end_date=end_date)

# Run the scheduler
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)  # Check for pending tasks every second

# Main function to start the scheduler in a separate thread
if __name__ == "__main__":
    # Load config
    configs = load_config_from_db()

    # Schedule tasks
    schedule_tasks_from_db(configs)

    # Run the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()

    # Keep the main thread alive
    while True:
        time.sleep(1)
