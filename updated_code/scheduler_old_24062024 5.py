import schedule
import time
import threading
import sys
import os
import logging
import signal
from functools import partial
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from fpdf import FPDF
import gridfs
import json

# Importing the functions directly
from openai_letter_generation import run_letter_generation
from Leave_acc_process import Leave_acc_main
from email_sending import send_email_now
from Goals_assign import assign_goal
from course_job_code import assign_courses
from renew_courses import check_and_renew_courses
from course_assign import assign_existing_employee_course
from process_learning_alerts import sync_instructor_led_training_for_learning
from process_learning_alerts import process_learning_alerts
from process_learning_alerts import process_learning_records
from process_learning_alerts import process_learning_recommendations
from process_learning_alerts import mass_assign_goals
from Calendar_Details_from_teams import fetch_calendar_events
from course_reassign import reassign_courses
from process_learning_alerts import course_recommendation
from process_learning_alerts import approval

# Database setup
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
db = client['PCL_Interns']
process_details_collection = db['Results_Collection']
client_collection = db['Client_Collection2']
processes_collection = db['Processes_Collection2']
fs = gridfs.GridFS(db)

# Ensure an index on Completion Time in descending order
process_details_collection.create_index([('Completion Time', DESCENDING)])

# Load letters configuration
with open('letters_config.json', 'r') as file:
    letters_config = json.load(file)

# Global variable to store currently scheduled jobs
scheduled_jobs = {}

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

# Load configuration from database
def load_config_from_db():
    return list(client_collection.find())

# Get parameters from the PopulationFilters in the collection, only keeping filled parameters
def get_parameters_from_population_filters(process_id):
    process = client_collection.find_one({'Process ID': process_id})
    if process and 'basic_options' in process:
        population_filters = process['basic_options'].get('population_filters', {})
        filled_parameters = {k: v for k, v in population_filters.items() if v}
        return filled_parameters
    return {}

# Setup logging
def setup_logging(process_name):
    logger = logging.getLogger(process_name)
    log_filename = f"{process_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_filepath = os.path.join('logs', log_filename)
    
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger.setLevel(logging.DEBUG)
    
    if logger.hasHandlers():
        logger.handlers.clear()

    fh = logging.FileHandler(log_filepath)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%a %b %d %H:%M:%S UTC %Y')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    return log_filepath, logger, fh

# Create PDF report with parameters
def create_report_pdf(parameters, task_name, file_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_margins(10, 10, 10)

    pdf.cell(200, 10, f"Task: {task_name}", ln=True)
    pdf.cell(200, 10, "Parameters:", ln=True)
    for key, value in parameters.items():
        pdf.cell(200, 10, f"{key}: {value}", ln=True)

    if not os.path.exists('reports'):
        os.makedirs('reports')
    pdf.output(os.path.join('reports', file_name))

# Read log file
def read_log_file(log_filepath):
    with open(log_filepath, 'r') as file:
        return file.read()

# Run the task and create a new entry for each cycle
def run_task(task_func, params, task_name, process_name, interval, unit, process_id, letter_config=None, letterhead_image_path=None):
    print(params, task_name)
    process_details_collection = db['Results_Collection']

    # Fetch all parameters from Client_Collection
    client_data = client_collection.find_one({'Process ID': process_id})
    all_parameters = client_data.get('basic_options') if client_data else {}

    process_details_id = ObjectId()
    start_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    next_scheduled_time = get_next_scheduled_time(interval, unit).strftime('%Y-%m-%dT%H:%M:%SZ')

    log_filepath, logger, log_handler = setup_logging(task_name)
    
    final_document = {
        "Process Name": process_name,
        "Function Name": task_name,
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
        "Log Details": ""
    }
    process_details_collection.insert_one(final_document)
    try:
        logger.info(f"Executing {task_name} with parameters {params}")
        # Initialize status
        status = 'Running'
        print(task_name)
        if task_name == 'run_letter_generation':
            status = run_letter_generation(params, letter_config, letterhead_image_path, db, process_details_id)
        elif task_name in ('Leave_acc_main'):
            status = Leave_acc_main(params, process_details_id, db)
        elif task_name == 'assign_goal':
            status = assign_goal(params, process_details_id, db)
        elif task_name == 'send_email_now':
            status = send_email_now()
        elif task_name == 'assign_courses':
            status = assign_courses()
        elif task_name == 'check_and_renew_courses':
            status = check_and_renew_courses(params)
        elif task_name == 'sync_instructor_led_training_for_learning':
            status = sync_instructor_led_training_for_learning()
        elif task_name == 'process_learning_alerts':
            status = process_learning_alerts()
        elif task_name == 'process_learning_records':
            status = process_learning_records()
        elif task_name == 'process_learning_recommendations':
            status = process_learning_recommendations()
        elif task_name == 'mass_assign_goals':
            status = mass_assign_goals()
        elif task_name == 'assign_existing_employee_course':
            status = assign_existing_employee_course(params, process_details_id, db)
        # elif task_name == 'fetch_calendar_events':
        #     status = fetch_calendar_events(params)
        elif task_name == 'reassign_courses':
            status = reassign_courses(params, db)
        elif task_name == 'course_recommendation':
            status = course_recommendation()
        elif task_name == 'approval':
            status = approval() 
              
        logger.info(f"Task {task_name} completed with status: {status}")

    except Exception as e:
        status = 'Failed'
        logger.error(f"Error running task {task_name}: {e}")

    finally:
        for handler in logger.handlers:
            handler.flush()

        logger.removeHandler(log_handler)
        log_handler.close()

        # Convert log file to txt and pdf
        txt_log_filepath = log_filepath.replace('.log', '.txt')
        os.rename(log_filepath, txt_log_filepath)
        
        pdf_filename = f"{task_name.replace(' ', '_')}_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        create_report_pdf(all_parameters, task_name, pdf_filename)

        process_details_collection.update_one(
            {'_id': final_document['_id']},
            {'$set': {
                'Completion Time': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'Status': status,
                'Log Details': read_log_file(txt_log_filepath)
            }}
        )

        final_document = process_details_collection.find_one({'_id': final_document['_id']})

        if status in ['Completed', 'Failed']:
            # Upload to GridFS
            with open(txt_log_filepath, 'rb') as log_file:
                fs.put(log_file, filename=os.path.basename(txt_log_filepath))
            with open(os.path.join('reports', pdf_filename), 'rb') as pdf_file:
                fs.put(pdf_file, filename=os.path.basename(pdf_filename))
            
            process_details_collection.update_one(
                {'_id': final_document['_id']},
                {'$set': {'Attachment File': {
                    "log": txt_log_filepath,
                    "report": os.path.join('reports', pdf_filename),
                    "log_details": read_log_file(txt_log_filepath)
                }}}
            )

        logger.handlers.clear()

def schedule_task_with_end_check(task_func_with_params, end_date):
    if datetime.now(timezone.utc) <= end_date:
        run_in_thread(task_func_with_params)

def run_in_thread(task_func_with_params):
    task_thread = threading.Thread(target=task_func_with_params)
    task_thread.start()
    return task_thread

def schedule_tasks_from_db(configs):
    global scheduled_jobs
    threads = []
    for config in configs:
        process_info = processes_collection.find_one({'process_name': config['process_name']})
        if not process_info:
            logging.warning(f"Process '{config['process_name']}' not found in Processes collection. Skipping.")
            continue
        
        function_name = process_info.get('function_name')
        if function_name not in globals():
            logging.error(f"Function '{function_name}' is not defined. Skipping.")
            continue
        
        process_id = config['Process ID']
        params = get_parameters_from_population_filters(process_id)
        print(f"Parameters for {function_name}: {params}")
        
        schedule_data = config['advanced_options']['schedule']
        task_func_partial = partial(
            run_task, 
            globals()[function_name], 
            params, 
            task_name=function_name,
            process_name = process_info.get('process_name'),
            interval=0, 
            unit='second', 
            process_id=process_id,
            letter_config=letters_config if function_name == 'run_letter_generation' else None,
            letterhead_image_path=r'letterhead.png' if function_name == 'run_letter_generation' else None
        )
        
        if 'as_soon_as_possible' in schedule_data:
            job = schedule.every().second.do(run_in_thread, task_func_partial)
            scheduled_jobs[process_id] = job
            threads.append(run_in_thread(task_func_partial))
        elif 'using_a_schedule' in schedule_data:
            frequency = schedule_data['using_a_schedule']['frequency']
            for freq_type, freq_details in frequency.items():
                if freq_type == 'once':
                    start_date = datetime.fromisoformat(freq_details['start_date']).replace(tzinfo=timezone.utc)
                    if datetime.now(timezone.utc) <= start_date:
                        job = schedule.every().second.at(start_date).do(run_in_thread, task_func_partial)
                        scheduled_jobs[process_id] = job
                elif freq_type == 'hourly_minute':
                    start_date = datetime.fromisoformat(freq_details['start_date']).replace(tzinfo=timezone.utc)
                    end_date = datetime.fromisoformat(freq_details['end_date']).replace(tzinfo=timezone.utc)
                    interval = int(freq_details['time_between_runs'].split()[0])
                    unit = freq_details['time_between_runs'].split()[1].lower()
                    if unit == 'minute':
                        job = schedule.every(interval).minutes.do(schedule_task_with_end_check, task_func_partial, end_date=end_date)
                        scheduled_jobs[process_id] = job
                    elif unit == 'second':
                        job = schedule.every(interval).seconds.do(schedule_task_with_end_check, task_func_partial, end_date=end_date)
                        scheduled_jobs[process_id] = job
                    elif unit == 'hour':
                        job = schedule.every(interval).hours.do(schedule_task_with_end_check, task_func_partial, end_date=end_date)
                        scheduled_jobs[process_id] = job
                elif freq_type == 'daily':
                    start_date = datetime.fromisoformat(freq_details['start_date']).replace(tzinfo=timezone.utc)
                    end_date = datetime.fromisoformat(freq_details['end_date']).replace(tzinfo=timezone.utc)
                    interval = int(freq_details['days_between_runs'])
                    job = schedule.every(interval).days.do(schedule_task_with_end_check, task_func_partial, end_date=end_date)
                    scheduled_jobs[process_id] = job
                elif freq_type == 'weekly':
                    start_date = datetime.fromisoformat(freq_details['start_date']).replace(tzinfo=timezone.utc)
                    end_date = datetime.fromisoformat(freq_details['end_date']).replace(tzinfo=timezone.utc)
                    interval = int(freq_details['weeks_between_runs'])
                    job = schedule.every(interval).weeks.do(schedule_task_with_end_check, task_func_partial, end_date=end_date)
                    scheduled_jobs[process_id] = job
                elif freq_type == 'monthly':
                    start_date = datetime.fromisoformat(freq_details['start_date']).replace(tzinfo=timezone.utc)
                    end_date = datetime.fromisoformat(freq_details['end_date']).replace(tzinfo=timezone.utc)
                    if 'repeat_by_day' in freq_details:
                        week_of_month = freq_details['repeat_by_day']['week_of_the_month']
                        day_of_week = freq_details['repeat_by_day']['day_of_the_week']
                        job = schedule.every().month.at(f'{week_of_month} {day_of_week}').do(schedule_task_with_end_check, task_func_partial, end_date=end_date)
                        scheduled_jobs[process_id] = job
                    elif 'repeat_by_date' in freq_details:
                        date = int(freq_details['repeat_by_date']['date'])
                        job = schedule.every().month.at(f'{date}').do(schedule_task_with_end_check, task_func_partial, end_date=end_date)
                        scheduled_jobs[process_id] = job
                elif freq_type == 'yearly':
                    start_date = datetime.fromisoformat(freq_details['start_date']).replace(tzinfo=timezone.utc)
                    end_date = datetime.fromisoformat(freq_details['end_date']).replace(tzinfo=timezone.utc)
                    month = int(freq_details['month'])
                    if 'repeat_by_day' in freq_details:
                        week_of_month = freq_details['repeat_by_day']['week_of_the_month']
                        day_of_week = freq_details['repeat_by_day']['day_of_the_week']
                        job = schedule.every().year.at(f'{month} {week_of_month} {day_of_week}').do(schedule_task_with_end_check, task_func_partial, end_date=end_date)
                        scheduled_jobs[process_id] = job
                    elif 'repeat_by_date' in freq_details:
                        date = int(freq_details['repeat_by_date']['date'])
                        job = schedule.every().year.at(f'{month}-{date}').do(schedule_task_with_end_check, task_func_partial, end_date=end_date)
                        scheduled_jobs[process_id] = job
    return threads

def update_scheduled_tasks():
    global scheduled_jobs
    while True:
        configs = load_config_from_db()
        current_job_ids = set(scheduled_jobs.keys())
        new_job_ids = {config['Process ID'] for config in configs}

        # Remove jobs that are no longer needed
        for job_id in current_job_ids - new_job_ids:
            schedule.cancel_job(scheduled_jobs[job_id])
            del scheduled_jobs[job_id]

        # Add new or updated jobs
        for config in configs:
            process_id = config['Process ID']
            if process_id not in scheduled_jobs:
                schedule_tasks_from_db([config])

        # Check for updates every 30 seconds
        time.sleep(5)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

def signal_handler(signal, frame):
    print("Received signal to shut down. Exiting...")
    sys.exit(0)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    configs = load_config_from_db()
    print(configs)

    scheduler_threads = []
    for config in configs:
        scheduler_threads.extend(schedule_tasks_from_db([config]))

    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()

    update_thread = threading.Thread(target=update_scheduled_tasks)
    update_thread.start()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down...")
        for t in scheduler_threads:
            t.join()
        scheduler_thread.join()
        update_thread.join()
        print("Shutdown complete.")
