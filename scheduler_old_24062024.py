import schedule
import time
import threading
import sys
import os
import logging
from functools import partial
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from fpdf import FPDF
import gridfs

# Database setup
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
db = client['PCL_Interns']
process_details_collection = db['Results_Collection']
client_collection = db['Client_Collection2']
processes_collection = db['Processes_Collection2']
fs = gridfs.GridFS(db)

# Ensure an index on Completion Time in descending order
process_details_collection.create_index([('Completion Time', DESCENDING)])

# Add tasks directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'tasks')))

# Import tasks from separate files
from generate_letters import generate_letters
from generate_notifications import generate_notifications
from assign_courses import assign_courses
from Leave_acc_process import Leave_acc_main

# Map task names to functions
TASKS = {
    'generate_letters': generate_letters,
    'generate_notifications': generate_notifications,
    'assign_courses': assign_courses,
    'Leave_acc_main': Leave_acc_main
}

# Load configuration from database
def load_config_from_db():
    return list(client_collection.find())

# Get parameters from the PopulationFilters in the collection
def get_parameters_from_population_filters(process_id):
    process = client_collection.find_one({'Process ID': process_id})
    if process and 'PopulationFilters' in process:
        population_filters = process['PopulationFilters']
        print('population_filters:',population_filters)
        # params = [value for key, value in population_filters.items() if value]
        # print('params:',params)
        return population_filters
    return []


# Function to get parameters from the PopulationFilters in the collection and return as JSON
# def get_parameters_from_population_filters(process_id):
#     process = client_collection.find_one({'Process ID': process_id})
#     if process and 'PopulationFilters' in process:
#         population_filters = process['PopulationFilters']
#         return population_filters
#     return {}

# def get_parameters_from_population_filters(process_id):
#     process = client_collection.find_one({'Process ID': process_id})
#     if process and 'PopulationFilters' in process:
#         population_filters = process['PopulationFilters']
        
#         # Ensure the keys and values are correctly formatted
#         formatted_filters = {}
#         for key, value in population_filters.items():
#             if value:  # Only include non-empty values
#                 formatted_filters[key] = value
                
#         return formatted_filters
#     return {}

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
        return now + relativedelta(months=interval)  # Exact interval for months
    elif unit == 'year':
        return now + relativedelta(years=interval)  # Exact interval for years
    else:
        return now

# Setup logging
def setup_logging(process_name):
    logger = logging.getLogger(process_name)
    log_filename = f"{process_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_filepath = os.path.join('logs', log_filename)
    
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger.setLevel(logging.DEBUG)
    
    # Clear previous handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    fh = logging.FileHandler(log_filepath)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%a %b %d %H:%M:%S UTC %Y')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    return log_filepath, logger, fh

# Convert log file to PDF
def convert_log_to_pdf(log_filepath):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_margins(10, 10, 10)
    
    # Add the log details to the PDF
    with open(log_filepath, 'r') as file:
        for line in file:
            pdf.multi_cell(0, 10, txt=line, align='L')
    
    pdf_filepath = log_filepath.replace('.log', '.pdf')
    pdf.output(pdf_filepath)
    
    return pdf_filepath

# Read log file
def read_log_file(log_filepath):
    with open(log_filepath, 'r') as file:
        return file.read()

# Run the task and create a new entry for each cycle
def run_task(task_func, *params, task_name, interval, unit, attachment_file, process_id):
    process_details_collection = db['Results_Collection']

    # Fetch all parameters from Client_Collection
    client_data = client_collection.find_one({'Process ID': process_id})
    all_parameters = client_data if client_data else {}

    # Generate a new process_details_id for each run
    process_details_id = ObjectId()
    start_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    next_scheduled_time = get_next_scheduled_time(interval, unit).strftime('%Y-%m-%dT%H:%M:%SZ')

    # Setup logging
    log_filepath, logger, log_handler = setup_logging(task_name)
    
    # Create a new process details document for this run
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

    # Execute the task with the latest parameters
    task_start_time = datetime.now(timezone.utc)
    try:
        logger.info(f"Executing {task_name} with parameters {params}")
        task_func(*params, process_details_id=process_details_id, db=db)
        status = 'Completed'
        logger.info(f"Process {task_name} completed successfully.")
    except Exception as e:
        status = 'Failed'
        logger.error(f"Error running task {task_name}: {e}")

    # Flush logging handlers to ensure log file is written
    for handler in logger.handlers:
        handler.flush()
    
    # Remove the log handler from the logger to release the file
    logger.removeHandler(log_handler)
    log_handler.close()

    # Update the process details document with completion info
    process_details_collection.update_one(
        {'_id': final_document['_id']},
        {'$set': {
            'Completion Time': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'Status': status,
            'Log Details': read_log_file(log_filepath)
        }}
    )

    # Regenerate the final document with updated info
    final_document = process_details_collection.find_one({'_id': final_document['_id']})

    # Generate PDF only if status is "Completed" or "Failed"
    if status in ['Completed', 'Failed']:
        pdf_filepath = convert_log_to_pdf(log_filepath)
        pdf_filename = os.path.basename(pdf_filepath)
        with open(pdf_filepath, 'rb') as pdf_file:
            fs.put(pdf_file, filename=pdf_filename)
        
        # Update the process details document with PDF file name
        process_details_collection.update_one(
            {'_id': final_document['_id']},
            {'$set': {'Attachment File': pdf_filename}}
        )

        # Delete the log file after creating the PDF
        os.remove(log_filepath)

    # Clear log handlers after updating the document
    logger.handlers.clear()

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
        # Check if the process exists in the Processes collection
        process_info = processes_collection.find_one({'Process Name': config['Process Name']})
        if not process_info:
            logging.warning(f"Process '{config['Process Name']}' not found in Processes collection. Skipping.")
            continue
        
        # Fetch the function name from Processes collection and map to actual function
        function_name = process_info.get('Function Name')
        task_func = TASKS.get(function_name)
        if not task_func:
            logging.warning(f"No task function found for '{function_name}'. Skipping.")
            continue
        
        # Fetch parameters from PopulationFilters in Client_Collection
        process_id = config['Process ID']
        params = get_parameters_from_population_filters(process_id)
        
        schedule_data = config['AdvancedOptions']['Schedule']

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
                        schedule.every(interval).minutes.do(schedule_task_with_end_check, partial(run_task, task_func, params, task_name=config['Process Name'], interval=interval, unit='minute', attachment_file="", process_id=process_id), end_date=end_date)
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
    print(configs)

    # Schedule tasks
    schedule_tasks_from_db(configs)

    # Run the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()

    # Keep the main thread alive
    while True:
        time.sleep(1)