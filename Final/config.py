
alert = {
    "goal_deadline_alert_days": [30, 15, 7, 1],  # Days before goal deadline to send alerts
    "task_deadline_alert_days": [14, 7, 3, 1],   # Days before task deadline to send alerts
    "from_email": "piyushbirkh@gmail.com",         # Replace with your email
    "ps": "teaz yfbj jcie twrt",          # Replace with your company name
    "company_name": "CJVCVWDUVC"
}


MONGODB_URI = "mongodb://localhost:27017/testing"
DATABASE_NAME = "testing"

COLLECTIONS = {
    "goal_plan_collection": "PGM_goal_plan",
    "review_period_collection": "PGM_review_period",
    "performance_document_types_collection": "PGM_performance_document_types",
    "goals_collection": "PGM_goal",
    "employee_details_collection": "HRM_employee_details",
    "employee_personal_details_collection": "HRM_personal_details",
    "employee_salary_details_collection": "HRM_salary_details",
    "my_goals_collection": "PGM_my_goals",
    "derived_employee_collection": "HRM_employee_derived_details",
    "eligibility_profiles_collection": "PGM_eligibility_profiles",
    "my_goals_plan_collection": "PGM_my_goal_plan_goals",
    "goal_offering_collection": "PGM_goal_offering",
    "mass_assign": "PGM_mass_assign_process",
    "goals_created_by_employees": "PGM_goals_created_by_employees",
    "email_queue": "SCH_email_queue",
    "email_template":"SCH_email_template"
}

#goal_plan schema to check whether given input is in correct format or not 
schemagp = {
        "type": "object",
        "properties": {
            "details": {
                "type": "object",
                "properties": {
                    "goal_plan_name": {"type": "string"},
                    "review_period": {"type": "string"},
                    "description": {"type": "string"},
                    "allow_updates_to_goals_by": {"type": "string"},
                    "actions_for_workers_and_managers_on_hr_assigned_goals": {"type": "string"},
                    "performance_document_type": {"type": "string"},
                    "evaluation_type": {"type": "string"},
                    "goal_weights": {"type": "string"},
                    # "maximum_goals_for_this_goal_plan": {"type": "string"},
                    "start_date": {"type": "string", "format": "date"},
                    "end_date": {"type": "string", "format": "date"}
                },
                "required": ["goal_plan_name", "review_period", "performance_document_type", "description", "start_date", "end_date"]
            },
            "goals": {
                "type": "array",
                "items": {"type": "string"}
            },
            "eligibility_profiles": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                    },
                    "required": ["name"]
                }
            },
            "included_workers": {
                "type": "array",
                "items": {"type": "string"}
            },
            "excluded_workers": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["details", "goals", "included_workers", "excluded_workers"]
    }

#goal schema to check whether given input is in correct format or not 
goal_schema = {
    "type": "object",
    "properties": {
        "basic_info": {
            "type": "object",
            "properties": {
                "goal_name": {"type": "string"},
                "description": {"type": "string"},
                "start_date": {"type": "string", "format": "date"},
                "target_completion_date": {"type": "string", "format": "date"},
                "category": {"type": "string"},
                "success_criteria": {"type": "string"},
                "status": {"type": "string"},
                "level": {"type": "string"},
                "subtype": {"type": "string"}
            },
            "required": ["goal_name", "description", "start_date", "target_completion_date", "category", "success_criteria", "status", "level", "subtype"]
        },
        "measurements": {
            "type": "array",  # Define measurements as an array
            "items": {  # Each item in the array should be an object with the following structure
                "type": "object",
                "properties": {
                    "measurement_name": {"type": "string"},
                    "unit_of_measure": {"type": "string"},
                    "start_date": {"type": "string", "format": "date"},
                    "end_date": {"type": "string", "format": "date"},
                    "comments": {"type": "string"},
                    "target_type": {"type": "string"},
                    "target_value": {"type": "string"},
                    "actual_value": {"type": "string"}
                },
                "required": ["measurement_name", "unit_of_measure", "start_date", "end_date", "comments", "target_type", "target_value", "actual_value"]
            }
        },
        "tasks": {
            "type": "array",  # Define tasks as an array
            "items": {  # Each item in the array should be an object with the following structure
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "status": {"type": "string"},
                    "priority": {"type": "string"},
                    "comments": {  # Define comments as an array of strings
                        "type": "array",
                        "items": {"type": "string"}
                    },
                   "completion_percentage": {"type": "string"},
                   "start_date": {"type": "string", "format": "date"},
                   "target_completion_date": {"type": "string", "format": "date"},
                   "related_link": {  # Define related links as an array of URIs
                        "type": "array",
                        "items": {"type": "string", "format": "uri"}
                    }
               },
           "required": ["name", "type", "status", "priority", "completion_percentage", "start_date", "target_completion_date"]  # Optional fields are not required
            }
        }
    },
    "required": ["basic_info", "measurements", "tasks"]#"eligibility_profiles"]
}

# Helper function to convert keys to lowercase and replace spaces with underscores
# This function is recursive, works for both dictionaries and lists
def lowercase_keys(data):
    if isinstance(data, dict):
        # For dictionary, convert keys and apply recursively
        return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        # For list, apply recursively on all elements
        return [lowercase_keys(item) for item in data]
    else:
        return data # Base case: return the data if neither dict nor list

# Define allowed fields for measurements
allowed_measurement_fields = {
    "measurement_name",
    "unit_of_measure",
    "start_date",
    "end_date",
    "comments",
    "target_type",
    "target_value",
    "actual_value"
    }

# Define allowed fields for tasks (if you also want to restrict fields for tasks)
allowed_task_fields = {
    "name",
    "type",
    "status",
    "priority",
    "comments",
    "completion_percentage",
    "start_date",
    "target_completion_date",
    "related_link"
    }