



1.  http://127.0.0.1:5000/eligibility_profiles/create


   {
  "create_participant_profile": {
    "eligibility_profile_definition": {
      "name": "Standard Eligibility",
      "description": "Eligibility criteria for performance management",
      "assignment_to_use": "Primary",
      "status": "Active",
      "view_hierarchy": "Flat",
      "profile_type": "Employee",
      "profile_usage": "Performance Management"
    },
    "eligibility_criteria": {
      "personal": {
        "gender": "Male",
        "disabled": "No",
        "postal_code_ranges": "All",
        "opted_for_medicare": "No",
        "leave_of_absence": "No",
        "termination_reason": "N/A",
        "qualification": "N/A",
        "competency": "All",
        "marital_status": "All",
        "religion": "All",
        "home_location": "Global",
        "person_type": "Employee",
        "service_areas": "All",
        "uses_tobacco": "No"
      },
      "employment": {
        "assignment_status": "Active",
        "hourly_or_salaried": "Both",
        "assignment_category": "All",
        "grade": "Senior",
        "job": "All",
        "position": "All",
        "payroll": "All",
        "salary_basis": "All",
        "department": "Development",
        "legal_entities": "All",
        "performance_rating": "All",
        "quartile_in_range": "All",
        "work_location": "All",
        "range_of_scheduled_hours": "All",
        "people_manager": "Yes",
        "job_function": "All",
        "job_family": "All",
        "hire_date": "All",
        "probation_period": "N/A",
        "business_unit": "IT"
      },
      "derived_factors": {
        "age": "All",
        "length_of_service": "All",
        "compensation": "All",
        "hours_worked": "All",
        "full_time_equivalent": "All",
        "combined_age_and_length_of_service": "All"
      },
      "other": {
        "benefit_groups": "All",
        "health_coverage_selected": "N/A",
        "participation_in_another_plan": "N/A",
        "formula": "N/A",
        "user_defined_criteria": "N/A"
      },
      "labor_relations": {
        "bargaining_unit": "N/A",
        "labor_union_member": "N/A",
        "union": "N/A",
        "collective_agreement": "N/A"
      }
    }
  },
  "updated_by": "Admin"  
}





2.  http://127.0.0.1:5000/review_periods/create



   {
  "Name": "Project Alpha",
  "Description": "Initial phase of the alpha project.",
  "start_date": "2024-01-01",
  "end_date": "2024-06-30",
  "Status": "Completed",
  "Updated By": "User1"
}


   
 3. http://127.0.0.1:5000/performance_roles/add_role


   {
  "Name": "Project Supervisor",
  "Description": "Oversees project progress and deliverables.",
  "Role Type": "Supervisory",
  "Allow role to view worker, manager and participant ratings, comments and questionnaires": "Yes",
  "Status": "Active",
  "In Use": "Yes",
  "start_date": "2024-01-01",
  "end_date": "2024-06-30",
}


4. http://127.0.0.1:5000/performance_document_types/add


    {
  "name": "New Document Type",
  "description": "Description of the new document type",
  "status": "Active",
  "start_date": "2024-07-24",
  "end_date": "2050-12-31"
}



5.http://127.0.0.1:5000/feedback_templates/create

  
    {
  "Name": "Template A",
  "Comments": "Comments for Template A",
  "Status": "Active",
  "Template type": "Type A",
  "Include in performance document": "Yes",
  "Questionnaire": [
    "Question A1",
    "Question A2"
  ]
}



6. http://127.0.0.1:5000/eligibility_batch_process/add


    {
  "performance_document_name": "Annual Review 2023",
  "effective_as_of_date": "2023-01-01T00:00:00.000Z",
  "review_period": "Annual",
  "create_eligible_performance_document": "Yes",
  "purge_historic_performance_management_eligibility_status_data": "No",
  "purge_data_older_than": "2020-01-01T00:00:00.000Z"
}



7.  http://127.0.0.1:5000/check_in_template/add


   {
  "template_type": "Type A",
  "name": "Template A",
  "comments": "Comments for Template A",
  "status": "Active",
  "from_date": {
    "$date": "2023-01-01T00:00:00.000Z"
  },
  "to_date": {
    "$date": "2024-01-01T00:00:00.000Z"
  },
  "review_period": "Annual",
  "include_in_performance_document": "Yes",
  "check_in_content": [
    "Content A"
  ],
  "eligibility_profiles": [
    "Standard Eligibility 1",
    "Standard Eligibility 2"
  ]
}



8. http://127.0.0.1:5000/performance_process_flows/create
   
   
    {
        "name": "Annual Evaluation 360 1",
        "description": "Description of Annual Evaluation 360",
        "from_date": "2024-07-24",
        "to_date": "2050-12-31",
        "status": "Active",
        "tasks": [
            {
                "name":"Worker Self-Evaluation",
                "task_name_for_manafger_role":"Worker Self-Evaluation",
                "task_name_for_worker_role": "Worker Self-Evaluation"
            },
            {
                "name":"Manager Evaluation of Workers",
                "task_name_for_manafger_role":"Manager Evaluation of Workers"
            },
            {
               "name":"Manage Participant Feedback",
               "task_name_for_manafger_role":"Manage Participant Feedback",
               "task_name_for_worker_role": "Manage Participant Feedback"
            },
            {
                "name":"Share Performance Document",
                "task_name_for_manafger_role":"Share Performance Document",
                "task_name_for_worker_role": "Share Performance Document"
            }
        ]
}