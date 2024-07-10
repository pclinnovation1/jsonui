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
from openai_letter_generation import run_letter_generation
from Leave_acc_process import Leave_acc_main
from email_sending import send_email_now
from fpdf import FPDF
import gridfs
import json
import io

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

# Map task names to functions
TASKS = {
    'run_letter_generation': run_letter_generation,
    'Leave_acc_main': Leave_acc_main,
    'send_email_now': send_email_now
}

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
    log_stream = io.StringIO()

    logger.setLevel(logging.DEBUG)
    
    if logger.hasHandlers():
        logger.handlers.clear()

    sh = logging.StreamHandler(log_stream)
    sh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%a %b %d %H:%M:%S UTC %Y')
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    
    return log_stream, logger, sh

def convert_objectid_to_str(data):
    if isinstance(data, dict):
        return {k: convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(i) for i in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

# Create PDF report with parameters
def create_report_pdf(parameters, task_name, file_name, start_time, end_time, duration, status, log_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_margins(10, 10, 10)

    # Report Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Scheduler Task Report", ln=True, align='C')
    pdf.ln(10)
    
    # General Information
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "1. General Information:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Report Title: Scheduler Task Report", ln=True)
    pdf.cell(200, 10, f"Generation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(200, 10, "Prepared By: Automated Scheduler System", ln=True)
    pdf.ln(10)
    
    # Task Details
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "2. Task Details:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Task Name: {task_name}", ln=True)
    pdf.cell(200, 10, f"Description: {parameters.get('description', 'No description provided')}", ln=True)
    
    # Parameters
    pdf.cell(200, 10, "Parameters:", ln=True)
    pdf.set_font("Arial", size=10)
    parameters_json = json.dumps(parameters, indent=4)
    for line in parameters_json.splitlines():
        pdf.cell(200, 10, line, ln=True)
    
    pdf.ln(10)

    # Execution Details
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "3. Execution Details:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Start Time: {start_time}", ln=True)
    pdf.cell(200, 10, f"End Time: {end_time}", ln=True)
    pdf.cell(200, 10, f"Duration: {duration}", ln=True)
    pdf.cell(200, 10, f"Status: {status}", ln=True)
    pdf.cell(200, 10, f"Next Scheduled Time: {parameters.get('next_scheduled_time', 'Not Available')}", ln=True)
    pdf.ln(10)

    # Performance Metrics
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "4. Performance Metrics:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Execution Time: Detailed in log content", ln=True)
    pdf.cell(200, 10, "Resource Usage: Not Implemented", ln=True)
    pdf.ln(10)

    # Logs
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "5. Logs:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Log Summary: See attached log content", ln=True)
    pdf.cell(200, 10, f"Log File Links: {log_content}", ln=True)
    pdf.ln(10)

    pdf_output = pdf.output(dest='S').encode('latin1')  # Get PDF output as bytes
    return pdf_output

# Run the task and create a new entry for each cycle
def run_task(task_func, params, task_name, interval, unit, process_id, letter_config=None, letterhead_image_path=None):
    process_details_collection = db['Results_Collection']

    # Fetch all parameters from Client_Collection
    client_data = client_collection.find_one({'Process ID': process_id})
    all_parameters = client_data if client_data else {}

    process_details_id = ObjectId()
    start_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    next_scheduled_time = get_next_scheduled_time(interval, unit).strftime('%Y-%m-%dT%H:%M:%SZ')

    log_stream, logger, log_handler = setup_logging(task_name)
    
    final_document = {
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
        "Log Details": ""
    }
    process_details_collection.insert_one(final_document)

    try:
        logger.info(f"Executing {task_name} with parameters {params}")
        # Pass additional arguments for specific tasks
        if task_name == 'Generate Letter':
            status = task_func(params, letter_config, letterhead_image_path, db, process_details_id)
        elif task_name == 'Calculate Accruals and Balances':
            status = task_func(params, process_details_id=process_details_id, db=db)
            print(status)
        elif task_name == 'Email Sending':
            status = task_func()
            print(status)
        logger.info(f"Process {task_name} completed with status {status}.")
    except Exception as e:
        status = 'Failed'
        logger.error(f"Error running task {task_name}: {e}")

    finally:
        end_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        duration = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%SZ') - datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%SZ')
        
        logger.removeHandler(log_handler)
        log_handler.close()

        log_content = log_stream.getvalue()
        
        pdf_filename = f"{task_name.replace(' ', '_')}_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Convert parameters to JSON serializable format
        all_parameters = convert_objectid_to_str(all_parameters)

        pdf_output = create_report_pdf(all_parameters, task_name, pdf_filename, start_time, end_time, str(duration), status, log_content)

        process_details_collection.update_one(
            {'_id': final_document['_id']},
            {'$set': {
                'Completion Time': end_time,
                'Status': status,
                'Log Details': log_content
            }}
        )

        final_document = process_details_collection.find_one({'_id': final_document['_id']})

        if status in ['Completed', 'Failed']:
            # Upload log content to GridFS
            log_id = fs.put(log_content.encode('utf-8'), filename=f"{task_name.replace(' ', '_')}_log.txt")
            # Upload PDF report to GridFS
            with fs.new_file(filename=pdf_filename) as fp:
                fp.write(pdf_output)
                report_id = fp._id
            
            process_details_collection.update_one(
                {'_id': final_document['_id']},
                {'$set': {'Attachment File': {
                    "log": log_id,
                    "report": report_id,
                    "log_details": log_content
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
    threads = []
    for config in configs:
        process_info = processes_collection.find_one({'process_name': config['process_name']})
        if not process_info:
            logging.warning(f"Process '{config['process_name']}' not found in Processes collection. Skipping.")
            continue
        
        function_name = process_info.get('function_name')
        task_func = TASKS.get(function_name)
        if not task_func:
            logging.warning(f"No task function found for '{function_name}'. Skipping.")
            continue
        
        process_id = config['Process ID']
        params = get_parameters_from_population_filters(process_id)
        print(f"Parameters for {function_name}: {params}")
        
        schedule_data = config['advanced_options']['schedule']

        task_func_partial = partial(
            run_task, 
            task_func, 
            params, 
            task_name=config['process_name'], 
            interval=0, 
            unit='second', 
            process_id=process_id,
            letter_config=letters_config if function_name == 'run_letter_generation' else None,
            letterhead_image_path=r'letterhead.png' if function_name == 'run_letter_generation' else None
        )

        if 'as_soon_as_possible' in schedule_data:
            threads.append(run_in_thread(task_func_partial))
        elif 'using_a_schedule' in schedule_data:
            frequency = schedule_data['using_a_schedule']['frequency']
            for freq_type, freq_details in frequency.items():
                if freq_type == 'once':
                    start_date = datetime.fromisoformat(freq_details['start_date']).replace(tzinfo=timezone.utc)
                    if datetime.now(timezone.utc) <= start_date:
                        schedule.once().at(start_date).do(run_in_thread, task_func_partial)
                elif freq_type == 'hourly_minute':
                    start_date = datetime.fromisoformat(freq_details['start_date']).replace(tzinfo=timezone.utc)
                    end_date = datetime.fromisoformat(freq_details['end_date']).replace(tzinfo=timezone.utc)
                    interval = int(freq_details['time_between_runs'].split()[0])
                    unit = freq_details['time_between_runs'].split()[1].lower()
                    if unit == 'minute':
                        schedule.every(interval).minutes.do(schedule_task_with_end_check, task_func_partial, end_date=end_date)
                    elif unit == 'second':
                        schedule.every(interval).seconds.do(schedule_task_with_end_check, task_func_partial, end_date=end_date)
                    elif unit == 'hour':
                        schedule.every(interval).hours.do(schedule_task_with_end_check, task_func_partial, end_date=end_date)
                elif freq_type == 'daily':
                    start_date = datetime.fromisoformat(freq_details['start_date']).replace(tzinfo=timezone.utc)
                    end_date = datetime.fromisoformat(freq_details['end_date']).replace(tzinfo=timezone.utc)
                    interval = int(freq_details['days_between_runs'])
                    schedule.every(interval).days.do(schedule_task_with_end_check, task_func_partial, end_date=end_date)
                elif freq_type == 'weekly':
                    start_date = datetime.fromisoformat(freq_details['start_date']).replace(tzinfo=timezone.utc)
                    end_date = datetime.fromisoformat(freq_details['end_date']).replace(tzinfo=timezone.utc)
                    interval = int(freq_details['weeks_between_runs'])
                    schedule.every(interval).weeks.do(schedule_task_with_end_check, task_func_partial, end_date=end_date)
                elif freq_type == 'monthly':
                    start_date = datetime.fromisoformat(freq_details['start_date']).replace(tzinfo=timezone.utc)
                    end_date = datetime.fromisoformat(freq_details['end_date']).replace(tzinfo=timezone.utc)
                    if 'repeat_by_day' in freq_details:
                        week_of_month = freq_details['repeat_by_day']['week_of_the_month']
                        day_of_week = freq_details['repeat_by_day']['day_of_the_week']
                        schedule.every().month.at(f'{week_of_month} {day_of_week}').do(schedule_task_with_end_check, task_func_partial, end_date=end_date)
                    elif 'repeat_by_date' in freq_details:
                        date = int(freq_details['repeat_by_date']['date'])
                        schedule.every().month.at(f'{date}').do(schedule_task_with_end_check, task_func_partial, end_date=end_date)
                elif freq_type == 'yearly':
                    start_date = datetime.fromisoformat(freq_details['start_date']).replace(tzinfo=timezone.utc)
                    end_date = datetime.fromisoformat(freq_details['end_date']).replace(tzinfo=timezone.utc)
                    month = int(freq_details['month'])
                    if 'repeat_by_day' in freq_details:
                        week_of_month = freq_details['repeat_by_day']['week_of_the_month']
                        day_of_week = freq_details['repeat_by_day']['day_of_the_week']
                        schedule.every().year.at(f'{month} {week_of_month} {day_of_week}').do(schedule_task_with_end_check, task_func_partial, end_date=end_date)
                    elif 'repeat_by_date' in freq_details:
                        date = int(freq_details['repeat_by_date']['date'])
                        schedule.every().year.at(f'{month}-{date}').do(schedule_task_with_end_check, task_func_partial, end_date=end_date)
    return threads

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

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down...")
        for t in scheduler_threads:
            t.join()
        scheduler_thread.join()
        print("Shutdown complete.")
