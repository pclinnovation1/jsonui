
'''

1. http://127.0.0.1:5000/goals


 1)goal1 
{
  "basic_info": {
    "goal_name": "Improve Customer Satisfaction 1",
    "description": "Increase sales by 30% in the next quarter",
    "start_date": "2024-01-01",
    "target_completion_date": "2024-03-31",
    "category": "Sales",
    "success_criteria": "Achieve 30% increase in sales",
    "status": "In Progress",
    "level": "Company",
    "subtype": "Quarterly Goal"
  },
  "measurements": {
    "measurement_name": "Sales Growth",
    "unit_of_measure": "Percentage",
    "start_date": "2024-01-01",
    "end_date": "2024-03-31",
    "comments": "Monitor bi-weekly",
    "target_type": "Threshold",
    "target_value": "30",
    "actual_value": "20"
  },
  "tasks": {
    "name": "Identify new markets",
    "type": "Research",
    "status": "In Progress",
    "priority": "High",
    "comments": "Focus on emerging markets and existing markets",
    "completion_percentage": "25",
    "start_date": "2024-01-10",
    "target_completion_date": "2024-01-31",
    "related_link": "http://example.com/market-research"
  },
  "library_info": {
    "status": "Published",
    "type": "Public",
    "available_to": "All employees",
    "legal_employer": "ABC Corp",
    "business_unit": "Sales",
    "department": "Sales Department",
    "external_id": "GOAL12345"
  },
  "eligibility_name": "Eligibility Profile 10",
  "updated_by": "Unknown"
}


 2)goal2
 
 {
  "basic_info": {
    "goal_name": "Increase sales 1",
    "description": "Increase sales by 30% in the next quarter",
    "start_date": "2024-01-01",
    "target_completion_date": "2024-03-31",
    "category": "Sales",
    "success_criteria": "Achieve 30% increase in sales",
    "status": "In Progress",
    "level": "Company",
    "subtype": "Quarterly Goal"
  },
  "measurements": {
    "measurement_name": "Sales Growth",
    "unit_of_measure": "Percentage",
    "start_date": "2024-01-01",
    "end_date": "2024-03-31",
    "comments": "Monitor bi-weekly",
    "target_type": "Threshold",
    "target_value": "30",
    "actual_value": "20"
  },
  "tasks": {
    "name": "Identify new markets",
    "type": "Research",
    "status": "In Progress",
    "priority": "High",
    "comments": "Focus on emerging markets and existing markets",
    "completion_percentage": "25",
    "start_date": "2024-01-10",
    "target_completion_date": "2024-01-31",
    "related_link": "http://example.com/market-research"
  },
  "library_info": {
    "status": "Published",
    "type": "Public",
    "available_to": "All employees",
    "legal_employer": "ABC Corp",
    "business_unit": "Sales",
    "department": "Sales Department",
    "external_id": "GOAL12345"
  },
  "eligibility_name": "Eligibility Profile 1",
  "updated_by": "U"
}



****************************************************************************




//already collection is there so no need to use this  
2.  http://127.0.0.1:5000/eligibility_profiles
 
 
{
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
 
  },
  "updated_by": "Admin"  
}
 
***********************************************************************



3. http://127.0.0.1:5000/review_periods

{
    "review_period_name": "Annual 2024",
    "description": "Performance review for the year",
    "status": "Active",
    "period_start_date": "2024-01-01",
    "period_end_date": "2024-06-30",
    "updated_by": "Admin User"
}
 
*****************************************************************************

 

4. http://127.0.0.1:5000/goal_plans

{
  "details": {
    "goal_plan_name": "Annual Performance Plan 2024",
    "review_period": "Annual 2024",
    "description": "Updated yearly performance goals",
    "allow_updates_to_goals_by": "Employee, Manager",
    "actions_for_workers_and_managers_on_hr_assigned_goals": "Review, Comment",
    "performance_document_types": "Annual Review",
    "evaluation_type": "360 Review",
    "goal_weights": "Weight by priority",
    "maximum_goals_for_this_goal_plan": "10",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "updated_by": "Admin User"
  },
  "goals": ["Increase Sales 1","Improve Customer Satisfaction 1"
  ],
  "eligibility_profiles": [
    {
      "name": "Eligibility Profile 3"
    }
  ],
  "included_workers": [
    "John Doe",
    "Jane Smith"
  ],
  "excluded_workers": [
    "Christy Torres"
  ]
}



***************************************************************************************

//this is for my_goals_controller.py which will give us goals if this are eligible by goal eligibility 

5.  http://127.0.0.1:5000/assign_goals

{
  "goal_plan_name": "Annual Performance Plan 2024",
  "updated_by": "Guess"
}


*******************************************************************************************************
//goals assign by based on goal plan only

6. http://127.0.0.1:5000/my_goal_plan

{
  "goal_plan_name": "Annual Performance Plan 2024",
  "updated_by": "Don"
}



*******************************************************************************************

7. http://127.0.0.1:5000/add_goal

{
  "name": "Ruchi",
  "goal_plan_assigned": "N/A",
  "goal_name": "Increase Sales",
  "progress": "Not started",
  "measurement": "None",
  "comments": [],
  "feedback": [],
  "updated_by": "Ankit"
}


*********************************************************************************************


8. http://127.0.0.1:5000/mass_assign_goal

{
  "goal_plan_assigned": "N/A",
  "goal_name": "Effective time management",
  "progress": "Not started",
  "measurement": "None",
  "comments": [],
  "feedback": [],
  "updated_by": "You"
}



'''