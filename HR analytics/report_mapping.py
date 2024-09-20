# report_mapping.py



report_fields_mapping = {
    "Headcount Report": {
        "HRM_employee_details": ["person_name",
            "department", "position", 
            "business_title", "location", "location_code", 
            "organization_unit", "employment_status", "employment_type", 
            "effective_start_date", "effective_end_date", "manager_name"
        ],
        "HRM_personal_details": [
            "person_number", "person_name", "date_of_birth"
        ],
        "HRM_salary_details": [
             "person_name","fte"
        ]
    },
    "Turnover and Retention Report": {
        "HRM_employee_details": [
            "person_name", "department", "position", "location", 
            "organization_unit", "office", "effective_start_date",  # Common Fields
            "effective_end_date", "employment_status", "employment_type",  # Turnover Fields
            "manager_name"  # Optional Field
        ],
        "HRM_salary_details": [
            "person_name","base_salary"  # Optional Field
        ]
    },
    "Workforce Composition Report": {
        "HRM_employee_details": [
            "person_number",
            "person_name",
            "department",
            "employment_type",
            "position"
        ]
    },
    "New Hire Report": {
        "HRM_employee_details": [
            "person_number",
            "person_name",
            "department",
            "position",           # job title
            "location",
            "effective_start_date", # hire date
            "employment_type",
            "manager_name",        # manager
            "employment_status"
        ],
        "HRM_personal_details": [
            "person_number",
            "person_name",
            "gender"
        ],
        "HRM_salary_details": [
            "person_name",
            "salary_class"         # salary_band
        ]
    },
    "Onboarding Status Report": {
        "JRN_journey": [
            "category",
            "users.person_name",
            #"users.status",
            "users.tasks.task_name",
            "users.tasks.task_due_date",
            "users.tasks.task_completion_date",
            "users.tasks.status",
            "users.tasks.performer",
            "users.tasks.time_status"
        ],
        "HRM_employee_details": [
            "person_number",
            "person_name",
            "department",
            "employment_type",
            "position",
            "manager_name",
            "location",
            "effective_start_date"  # hire_date

        ]
    },
    "Learning Report": {
    "LRN_course_assignment": [
        "course_name", 
        "assignment_type", 
        "date_assignment", 
        "due_date", 
        "completion_date", 
        "person_name", 
        "timestamp"
    ]
        },
        
    "FMLA Report": {
    "ABS_leave_application": [
        "person_name",
        "leave_type",
        "start_date",          # leave_start_date
        "end_date",            # leave_end_date
        "duration",            # leave_duration
        "reason_for_absence",  # leave_reason
        "status"               # manager_approval (could represent approval status)
    ],
    "ABS_leave_balance": [
        "person_name",
        "leave_type",
        "leave_balance"
    ],
    "ABS_daily_leave_details": [
        "person_name",
        "leave_type",
        "date",                # date of the leave day
        "absence_type",        # type of absence (FMLA, vacation, etc.)
        "days"                 # number of days (could represent leave duration)
    ],
    "HRM_employee_details": ["person_name",
            "department", "position", 
            "business_title", "location", "location_code", 
            "organization_unit", "employment_status", "employment_type", "manager_name"
        ]
},

"Diversity and Inclusion Report": {
    "HRM_employee_details": [
        "person_number",
        "person_name",
        "department",
        "location",
        "employment_status",
        "employment_type"
    ],
    "HRM_personal_details": [
        "person_number",
        "person_name",
        "gender",
        "date_of_birth"
    ]
},
"Workforce Demographics Report": {
    "HRM_employee_details": [
        "person_number", 
        "person_name", 
        "employment_type", 
        "location"
    ],
    "HRM_personal_details": [
        "person_name", 
        "gender", 
        "date_of_birth"
    ]
},
"Disciplinary Action Report":{
    "disciplinary_actions": [
    "person_name",
    "action",
    "reason",
    "status",
    "event_date",
    "action_date",
    "action_by",
    "severity",
    "manager_name",
    "followup_tasks.task_description",
    "followup_tasks.due_date",
    "followup_tasks.status",
    "appeal_status",
    "acknowledged_at",
    "created_at",
    "updated_at"
]

}

}

