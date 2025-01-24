import json
import requests
import concurrent.futures
from flask import Flask, jsonify
from pymongo import MongoClient
import re

# Flask App initialization
app = Flask(__name__)

# Load configuration file
with open("config.json", "r") as config_file:
    CONFIG = json.load(config_file)

# MongoDB Configuration
MONGODB_URI = CONFIG["mongodb"]["uri"]
DATABASE_NAME = CONFIG["mongodb"]["database_name"]
COLLECTION_NAME = CONFIG["mongodb"]["API_absence"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

CONFIGURATION_MAPPING_ABSENCE = {
    "absence_entry_basic_flag": "absenceEntryBasicFlag",
    "absence_pattern_cd": "absencePatternCd",
    "absence_status_cd": "absenceStatusCd",
    "approval_status_cd": "approvalStatusCd",
    "auth_status_update_date": "authStatusUpdateDate",
    "blocked_leave_candidate": "blockedLeaveCandidate",
    "child_event_type_cd": "childEventTypeCd",
    "condition_start_date": "conditionStartDate",
    "confirmed_date": "confirmedDate",
    "consumed_by_agreement": "consumedByAgreement",
    "disease_code": "diseaseCode",
    "duration": "duration",
    "employee_shift_flag": "employeeShiftFlag",
    "absence_end_date": "endDate",
    "absence_end_date_duration": "endDateDuration",
    "absence_end_date_time": "endDateTime",
    "absence_end_time": "endTime",
    "establishment_date": "establishmentDate",
    "frequency": "frequency",
    "initial_timely_notify_flag": "initialTimelyNotifyFlag",
    "late_notify_flag": "lateNotifyFlag",
    "legislation_code": "legislationCode",
    "notification_date": "notificationDate",
    "object_version_number": "objectVersionNumber",
    "open_ended_flag": "openEndedFlag",
    "overridden": "overridden",
    "period_of_incap_to_work_flag": "periodOfIncapToWorkFlag",
    "planned_end_date": "plannedEndDate",
    "processing_status": "processingStatus",
    "project_id": "projectId",
    "single_day_flag": "singleDayFlag",
    "source": "source",
    "spl_condition": "splCondition",
    "absence_start_date": "startDate",
    "absence_start_date_duration": "startDateDuration",
    "absence_start_date_time": "startDateTime",
    "absence_start_time": "startTime",
    "submitted_date": "submittedDate",
    "timeliness_override_date": "timelinessOverrideDate",
    "unit_of_measure": "unitOfMeasure",
    "user_mode": "userMode",
    "person_number": "personNumber",
    "absence_type": "absenceType",
    "employer": "employer",
    "absence_reason": "absenceReason",
    "absence_disp_status": "absenceDispStatus",
    "agreement_name": "agreementName",
    "payment_detail": "paymentDetail",
    "assignment_name": "assignmentName",
    "assignment_number": "assignmentNumber",
    "unit_of_measure_meaning": "unitOfMeasureMeaning",
    "formatted_duration": "formattedDuration",
    "absence_disp_status_meaning": "absenceDispStatusMeaning",
    "absence_updatable_flag": "absenceUpdatableFlag",
    "approval_datetime": "ApprovalDatetime" 
}

# Function to map absence data
def map_absence_data(absence_item):
    return {key: absence_item.get(value, None) for key, value in CONFIGURATION_MAPPING_ABSENCE.items()}

def fetch_absence_data():
    absence_data = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_absence_chunk(offset):
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/absences?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_absence_chunk, offset) for offset in offsets]):
            absence_data.extend(future.result())
    return [map_absence_data(absence) for absence in absence_data]

def generate_report3():
    try:
        # Fetch absence data
        absence_data = fetch_absence_data()
        # Insert merged data into MongoDB
        collection.insert_many(absence_data)
        message = f"Inserted {len(absence_data)} absence records successfully."
        print(message)
        return message

        
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return f"Error fetching data: {e}"
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}"
