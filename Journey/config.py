# -------------------------------------------------------------------
# # MongoDB connection setup  
# MONGODB_URI = "mongodb://oras_user:oras_pass@172.191.245.199:27017/oras"
# DATABASE_NAME = "oras"




MONGODB_URI = "mongodb://localhost:27017/testing"
DATABASE_NAME = "testing"

JRN_journey="JRN_journey"
HRM_employee_details="HRM_employee_details"
JRN_task="JRN_task"
eligibility_profile_collection="PGM_eligibility_profiles"
email_template="SCH_email_template"
email_queue="SCH_email_queue"
employee_personal_details_collection= "HRM_personal_details"
employee_salary_details_collection= "HRM_salary_details"
derived_employee_collection="HRM_employee_derived_details"

JRN_boarding_category={
    "onboarding_category":"onboarding",
    "pre_onboarding_category":"pre_onboarding",
    "offboarding_cateogry":"offboarding"
}
templates= {
        'user_unassigned_from_journey': 'user_unassigned_from_journey',
        'task_removed_notification': 'task_removed_notification',
        'team_assignment_notification': 'team_assignment_notification',
        'user_added_to_journey': 'user_added_to_journey',
        'journey_updated': 'journey_updated',
        'team_task_complete': 'team_task_complete',
        'task_complete': 'task_complete',
        'employee_added_notification': 'employee_added_notification',
        'tasks_assigned': 'tasks_assigned',
        'onboarding_journey_assigned_today': 'onboarding_journey_assigned_today',
        'employee_offboarding': 'employee_offboarding',
        'team_creation_notification': 'team_creation_notification',
        'task_updated': 'task_updated',
        "tasks_overdue3":"tasks_overdue3",
        "task_removal_from_jrn_notification":"task_removal_from_jrn_notification"
}
others = {
    "HR_JOB_CODE":"JB10",
    "company_name":"ORAS",
}
