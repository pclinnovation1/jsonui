from pymongo import MongoClient
from datetime import datetime
import schedule
import time
import logging
import os

# Connect to MongoDB
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
db = client['PCL_Interns']

# Collections
processes_collection = db['Processes_Collection']
client_collection = db['Client_Collection']
results_collection = db['Results_Collection']

def fetch_process_parameters(process_name):
    try:
        parameters = client_collection.find_one({"Process Name": process_name})
        if parameters is None:
            print(f"No parameters found for {process_name}")
        else:
            print(f"Fetched parameters for {process_name}: {parameters}")
        return parameters
    except Exception as e:
        print(f"Error fetching parameters for {process_name}: {e}")
        return None

def setup_logging(process_name):
    log_filename = f"{process_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_filepath = os.path.join('logs', log_filename)
    
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logging.basicConfig(
        filename=log_filepath,
        level=logging.DEBUG,
        format='%(asctime)s: %(message)s',
        datefmt='%a %b %d %H:%M:%S UTC %Y'
    )
    return log_filepath

def read_log_file(log_filepath):
    with open(log_filepath, 'r') as file:
        return file.read()

def execute_process(process_name, parameters):
    log_filepath = setup_logging(process_name)
    
    try:
        logging.info(f"Executing {process_name} with parameters {parameters}")
        success = True  # Simulate a successful execution condition

        logging.info("Process started")
        logging.info("Processing event assignment")
        # Simulate processing steps here
        logging.info("Processing complete")

        if success:
            log_details = read_log_file(log_filepath)
            result = {
                "Process Name": process_name,
                "Status": "Completed",
                "Completion Time": datetime.now(),
                "Parameters Used": parameters,
                "Log Details": log_details  # Store log details
            }
            insert_result = results_collection.insert_one(result)
            logging.info(f"Process {process_name} completed successfully. Result ID: {insert_result.inserted_id}")
        else:
            logging.info(f"Process {process_name} failed.")
    except Exception as e:
        logging.error(f"Error executing {process_name}: {e}")
    finally:
        logging.shutdown()

def schedule_processes():
    try:
        processes = processes_collection.find({})
        for process in processes:
            process_name = process.get("Process Name")
            parameters = fetch_process_parameters(process_name)
            if parameters:
                schedule_info = parameters.get('AdvancedOptions', {}).get('Schedule', {}).get('UsingASchedule', {})
                if 'StartDate' in schedule_info:
                    start_time = schedule_info['StartDate']
                    if 'T' in start_time:
                        start_time = start_time.split('T')[1][:5]  # Extract time, assuming format 'YYYY-MM-DDTHH:MM:SS'
                    else:
                        start_time = '11:46'  # Default time if no time is provided
                    schedule.every().day.at(start_time).do(execute_process, process_name, parameters)
                    print(f"Scheduled {process_name} at {start_time}")
                else:
                    print(f"Skipping {process_name} due to missing or invalid schedule.")
    except Exception as e:
        print(f"Error scheduling processes: {e}")

# Run the scheduler
if __name__ == '__main__':
    # Direct test call to execute_process for immediate verification
    process_name = "Evaluate Certification Updates"
    parameters = fetch_process_parameters(process_name)
    if parameters:
        execute_process(process_name, parameters)

    # Schedule processes
    schedule_processes()
    while True:
        schedule.run_pending()
        time.sleep(1)
