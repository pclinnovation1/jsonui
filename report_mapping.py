# report_mapping.py
report_fields_mapping = {
    "Course Completion Report": {
        "fields": ["person_name", "course_name", "completion_date", "completed_status"],
        "collections": ["LRN_employee_offering_detail", "HRM_employee_details"]
    },
    "In-Progress Learning Report": {
        "fields": ["person_name", "course_name", "enrollment_date", "progress_percentage"],
        "collections": ["LRN_employee_offering_detail", "LRN_course"]
    },
    "Enrollment Report": {
        "fields": ["person_name", "course_name", "enrollment_date", "department", "job_title"],
        "collections": ["HRM_employee_details", "LRN_employee_offering_detail"]
    },
    "Compliance Training Completion Report": {
        "fields": ["person_name", "course_name", "completion_date", "compliance_status", "department", "job_title"],
        "collections": ["LRN_course_assignment", "HRM_employee_details"]
    },
    "Learning Engagement Report": {
        "fields": ["person_name", "course_name", "actual_effort"],
        "collections": ["LRN_employee_offering_detail"]
    },
    "Course Feedback Report": {
        "fields": ["person_name", "course_name", "feedback_rating", "feedback_comments"],
        "collections": ["LRN_course"]
    },
    "Return on Investment (ROI) Report": {
        "fields": ["training_cost", "person_name", "roi_calculation"],
        "collections": ["LRN_course", "HRM_employee_details"]
    },
    "Departmental Learning Overview": {
        "fields": ["department_name", "course_titles", "completion_rates", "completion_status"],
        "collections": ["HRM_employee_details"]
    },
    "Cross-Functional Reports": {
        "fields": ["employee_demographics", "learning_data"],
        "collections": ["HRM_employee_details", "LRN_course"]
    }
}
