import json
import requests
import concurrent.futures
from flask import Flask
from pymongo import MongoClient


# Flask App initialization
app = Flask(__name__)

# Load configuration file
with open("config.json", "r") as config_file:
    CONFIG = json.load(config_file)

# MongoDB Configuration
MONGODB_URI = CONFIG["mongodb"]["uri"]
DATABASE_NAME = CONFIG["mongodb"]["database_name"]
COLLECTION_NAME = CONFIG["mongodb"]["API_journeyTaskLibrary"]

# Initialize MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Mapping configuration for journeyTaskLibrary fields
CONFIGURATION_MAPPING_TASK_LIBRARY = {
    "task_level": "TaskLevel",
    "task_level_meaning": "TaskLevelMeaning",
    "task_level_value": "TaskLevelValue",
    "name": "Name",
    "type": "Type",
    "type_meaning": "TypeMeaning",
    "sub_type": "SubType",
    "sub_type_meaning": "SubTypeMeaning",
    "required_flag": "RequiredFlag",
    "status": "Status",
    "status_meaning": "StatusMeaning",
    "target_duration": "TargetDuration",
    "target_duration_uom": "TargetDurationUOM",
    "target_duration_uom_meaning": "TargetDurationUOMMeaning",
    "delay_duration": "DelayDuration",
    "delay_duration_uom": "DelayDurationUOM",
    "delay_duration_uom_meaning": "DelayDurationUOMMeaning",
    "description": "Description",
    "allow_note_title_flag": "AllowNoteTitleFlag",
    "allow_comment_flag": "AllowCommentFlag",
    "allow_attachment_flag": "AllowAttachmentFlag",
    "open_in_same_page_flag": "OpenInSamePageFlag",
    "open_report_in_same_page_flag": "OpenReportInSamePageFlag",
    "allow_notes_content_flag": "AllowNotesContentFlag",
    "note_title": "NoteTitle",
    "action_url": "ActionURL",
    "performer_type": "PerformerType",
    "performer_type_meaning": "PerformerTypeMeaning",
    "performer_user_group_code": "PerformerUserGroupCode",
    "performer_responsibility_type": "PerformerResponsibilityType",
    "performer_responsibility_type_meaning": "PerformerResponsibilityTypeMeaning",
    "performer_person_id": "PerformerPersonId",
    "owner_type": "OwnerType",
    "owner_type_meaning": "OwnerTypeMeaning",
    "owner_user_group_code": "OwnerUserGroupCode",
    "owner_responsibility_type": "OwnerResponsibilityType",
    "owner_responsibility_type_meaning": "OwnerResponsibilityTypeMeaning",
    "owner_person_id": "OwnerPersonId",
    "attachment_document_type_name": "AttachmentDocumentTypeName",
    "questionnaire_name": "QuestionnaireName",
    "configurable_form_context": "ConfigurableFormContext",
    "application_task": "ApplicationTask",
    "application_task_name": "ApplicationTaskName",
    "report_path": "ReportPath",
    "digital_signature_template_id": "DigitalSignatureTemplateId",
    "signature_validation_configuration": "SignatureValidationConfiguration",
    "work_authorization_configuration": "WorkAuthorizationConfiguration",
    "process_cloud_configuration": "ProcessCloudConfiguration",
    "learning_item_id": "LearningItemId",
    "learn_enrollment_id": "LearnEnrollmentId",
    "learn_enrollment_type": "LearnEnrollmentType",
    "embedded_application_task_code": "EmbeddedApplicationTaskCode",
    "embedded_application_task_type_id": "EmbeddedApplicationTaskTypeId",
    "content_provider_code": "ContentProviderCode",
    "learn_community_id": "LearnCommunityId",
    "learning_content_type": "LearningContentType",
    "learning_content_type_meaning": "LearningContentTypeMeaning",
    "video_type": "VideoType",
    "video_type_meaning": "VideoTypeMeaning",
    "video_url": "VideoURL",
    "analysis_path": "AnalysisPath",
    "analysis_parameters": "AnalysisParameters",
    "display_options": "DisplayOptions",
    "document_type_name": "DocumentTypeName",
    "save_documents_to_dor_for": "SaveDocumentsToDORFor",
    "save_documents_to_dor_for_meaning": "SaveDocumentsToDORForMeaning",
    "eligibility_profile_name": "EligibilityProfileName",
    "activation_eligibility_profile_id": "ActivationEligibilityProfileId",
    "activation_eligibility_profile_name": "ActivationEligibilityProfileName",
    "evaluation_offset": "EvaluationOffset",
    "enable_expiry_flag": "EnableExpiryFlag",
    "expiry_relative_to": "ExpiryRelativeTo",
    "expiry_relative_to_meaning": "ExpiryRelativeToMeaning",
    "expiry_duration": "ExpiryDuration",
    "reminder_duration": "ReminderDuration",
    "reminder_recurrence": "ReminderRecurrence",
    "reminder_relative_to": "ReminderRelativeTo",
    "reminder_relative_to_meaning": "ReminderRelativeToMeaning",
    "display_features": "DisplayFeatures",
    "save_attachments_to_dor_for": "SaveAttachmentsToDORFor",
    "save_attachments_to_dor_for_meaning": "SaveAttachmentsToDORForMeaning",
    "feed_flag": "FeedFlag",
    "initiated_feed_flag": "InitiatedFeedFlag",
    "reassigned_feed_flag": "ReassignedFeedFlag",
    "completed_feed_flag": "CompletedFeedFlag",
    "deleted_feed_flag": "DeletedFeedFlag",
    "created_by": "CreatedBy",
    "creation_date": "CreationDate",
    "last_updated_by": "LastUpdatedBy",
    "last_update_date": "LastUpdateDate",
    "action_complete_label": "ActionCompleteLabel",
    "action_reject_label": "ActionRejectLabel",
    "action_add_to_calendar_label": "ActionAddToCalendarLabel",
    "action_save_label": "ActionSaveLabel",
    "activity_action1_label": "ActivityAction1Label",
    "activity_action2_label": "ActivityAction2Label",
    "activity_action3_label": "ActivityAction3Label",
    "activity_action4_label": "ActivityAction4Label",
    "activity_action5_label": "ActivityAction5Label"
}


def map_task_library_data(task_item):
    """Map API response fields to MongoDB document fields for journeyTaskLibrary."""
    return {key: task_item.get(value, None) for key, value in CONFIGURATION_MAPPING_TASK_LIBRARY.items()}

def fetch_task_library():
    """Fetch task library data from the API."""
    task_library_data = []
    api_config = CONFIG["api"]
    offsets = list(range(
        CONFIG["offsets"]["range_start"],
        CONFIG["offsets"]["range_end"],
        CONFIG["offsets"]["step"]
    ))

    def fetch_task_library_chunk(offset):
        """Fetch a chunk of task library data."""
        url = f"{api_config['url']}/hcmRestApi/resources/11.13.18.05/journeyTaskLibrary?limit={api_config['limit']}&offset={offset}&onlyData=true"
        response = requests.get(url, auth=(api_config['username'], api_config['password']))
        response.raise_for_status()
        return response.json().get('items', [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for future in concurrent.futures.as_completed([executor.submit(fetch_task_library_chunk, offset) for offset in offsets]):
            task_library_data.extend(future.result())

    return task_library_data

def generate_report3():
    """Generate and store task library data report."""
    try:
        tasks = fetch_task_library()
        mapped_data = [map_task_library_data(task) for task in tasks]

        if mapped_data:
            collection.insert_many(mapped_data)
            message = f"Inserted {len(mapped_data)} journey task library records successfully."
        else:
            message = "No journey task library records found."
        print(message)
        return {"message": message}, 200

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return {"error": f"Error fetching data: {e}"}, 500
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": f"An error occurred: {e}"}, 500
