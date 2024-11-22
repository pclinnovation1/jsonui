import ast
from flask import Flask, jsonify
from pymongo import MongoClient
import os
from pprint import pprint
import re
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate  # Correct import for PromptTemplate
from langchain.chains import LLMChain  # Correct import for LLMChain
# Suppress Deprecation Warnings
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Flask App initialization
app = Flask(__name__)



# Prompts Definition
base_prompt = """
You are an intelligent assistant responsible for analyzing user prompts and generating relevant field names for various HR reports. Your job is to understand the user's prompt and provide only the relevant field names from the schemas listed below.
 
Here are the available schemas and fields you can work with:
 
HRM_employee_details schema:
    person_number: Unique ID assigned to the employee.
    person_name: Full name of the employee.
    organization_unit: The unit or department the employee belongs to.
    position: Job position or title of the employee.
    manager_name: Name of the employee's direct manager.
    employment_status: Current employment status (e.g., Active, Terminated).
    effective_start_date: Date the employee started in the current role.
    effective_end_date: Date the employee’s role or employment ended.
    business_unit: Business unit the employee belongs to.
    department: Department the employee is part of.
    working_hours: Number of hours worked per week.
    full_time_or_part_time: Indicates if the employee is full-time or part-time.
    fte: Full-time equivalent value.
    retirement_date: The employee's anticipated or actual retirement date.
    location: Physical location of the employee.
    working_as_manager: Indicates if the employee works as a manager.
    working_from_home: Indicates if the employee works remotely.
 
HRM_personal_details schema:
    person_number: Unique ID assigned to the employee.
    person_name: Full name of the employee.
    date_of_birth: Birthdate of the employee.
    home_country: Country where the employee resides.
    citizenship_status: Citizenship status of the employee.
    nationality: Nationality of the employee.
    gender: Gender of the employee.
 
HRM_salary_details schema:
    person_number: Unique ID assigned to the employee.
    person_name: Full name of the employee.
    base_salary: The employee's base salary.
    compensation: Total compensation for the employee, including base salary and benefits.
    salary_effective_date: The date the current salary took effect.
    currency: The currency in which the salary is paid.
    fte: Full-time equivalent value.
 
JRN_journey schema:
    - `journey_name`: The title or name of the journey (e.g., "Badge Request").
    - `category`: The category or type of the journey (e.g., "Badge_R").
    
    - `users`: A list of users associated with the journey. For each user, the following fields are included:
        - `person_name`: The name of the person participating in the journey.
        - `status`: The current status of the person in the journey (e.g., "In Progress", "Completed").
 
        - `tasks`: A list of tasks assigned to the user as part of the journey. For each task, the following fields are included:
            - `task_name`: The name or title of the task (e.g., "Request a Badge").
            - `status`: The current status of the task (e.g., "Not Started", "In Progress").
            - `task_start_date`: The date when the task started.
            - `task_due_date`: The date by which the task is due.
 
 
JRN_task schema:
    task_name: The name of the task.
    task_type: The type of task (e.g., Process Automation).
    performer: The role responsible for completing the task (e.g., Manager, Employee).
    owner: The owner of the task.
    description: A description of the task.
    task_link: A link to the task.
    duration: The task's duration.
    time_unit: The unit of time for the task (e.g., days, hours).
 
ABS_daily_leave_details schema:
    person_name: Name of the person taking leave.
    leave_type: The type of leave (e.g., Study Leave, Sick Leave).
    date: The date when the leave occurred.
    days: Number of leave days taken.
 
ABS_leave_application schema:
    person_name: Name of the person applying for leave.
    leave_type: The type of leave requested (e.g., Sick Leave, Vacation).
    start_date: Start date of the leave period.
    end_date: End date of the leave period.
    duration: Total duration of the leave.
    status: The current status of the leave application (e.g., approval required, approved).
 
ABS_leave_balance schema:
    person_name: Name of the person for whom leave balance is being tracked.
    leave_type: The type of leave (e.g., Sick Leave, Study Leave).
    leave_balance: The remaining balance of leave days.
 
TBI_workforce_data schema
    person_name: Name of the worker,
    email: E-mail of the worker,
    country_region: Country where the worker is located,
    processing_status: Whether the allocation has been processed or not,
    eligibility_status: Whether the worker is eligible for the compensation plan or not,
    date_of_birth: Date of birth in format YYYY-MM-DD,
    work_phone: Work phone number of worker,
    department: Department of the worker,
    location: City where the worker is located,
    job: Job profile of the worker,
    years_in_job: Time duration in years for which the worker has been working on the job profile,
    grade: Grade currently assigned to the worker,
    original_hire_date: Date on which the worker was hired in the company,
    primary_manager: Current primary manager of the worker,
    review_manager: Current manager who reviews the worker's tasks,
    secondary_manager: Current secondary manager of the worker,
    current_assignment_name: Currently assigned team of the worker,
    ars_employed: Years for which the worker has been working in the company,
    direct_manager: Current direct manager of the company,
    hierarchy_level: Hierarchy status of the worker,
    years_in_grade: Years for which the worker has been working in the grade,
    business_unit: Currently assigned business unit name of the worker,
    normal_hours: Normal working hours of the worker in a week,
    worker_number: A unique number/id assigned to the worker,
    position_change_date: Date on which the worker's position was changed,
    years_in_position: Years for which the worker has been working in the current position,
    position: The current job title of the worker.
    job_code: The code associated with the worker's current job.
    position_code: The unique code identifying the worker's position.
    working_hours: The number of hours the worker is expected to work per week.
    manager: The worker's direct manager or supervisor (if any).
    person_number: A unique identifier assigned to the worker.
    grade_code: The code representing the worker's grade within the organization.
    reassignment_date: The date on which the worker was reassigned to the current role.
    job_attribute_1: An additional attribute or characteristic related to the worker's job.
    assignment_status: The current status of the worker's assignment (e.g., Active, Inactive).
    assignment_category: The classification of the worker’s assignment (e.g., Full-Time, Part-Time).
    payroll: The frequency at which the worker receives their salary (e.g., Bi-Weekly).
    hire_date: The date the worker was originally hired by the company.
    reassigned_by: The person or department responsible for reassigning the worker.
    job_attribute_4: Another job-related attribute or characteristic.
    job_attribute_2: A second additional attribute or characteristic related to the worker's job.
    legal_employer: The legal entity that employs the worker.
    job_attribute_3: A third additional attribute or characteristic related to the worker's job.
    job_history: A list of previous jobs held by the worker within the organization.
    job_attribute_5: A fifth job-related attribute or characteristic.
    grade_change_date: The date on which the worker's grade was last changed.
    job_change_date: The date the worker's job role was last updated.
    job_attribute_6: A sixth job-related attribute or characteristic.
    base_salary_current: The worker's current base salary.
    base_salary_percentage_change: The percentage change in the worker's base salary.
    adjusted_salary_current: The current adjusted salary of the worker.
    adjusted_salary_new: The new adjusted salary proposed for the worker.
    adjusted_salary_change_amount: The difference in the worker's adjusted salary after the change.
    full_time_equivalent: A value representing the worker’s full-time equivalent status
    annualized_full_time_salary_current: The current annualized full-time salary of the worker.
    annualized_full_time_salary_new: The proposed new annualized full-time salary.
    annualized_full_time_salary_change_amount: The amount of change in the annualized full-time salary.
    salary_range_low_current: The current lowest value of the salary range for the worker's position.
    salary_range_high_current: The current highest value of the salary range for the worker's position.
    salary_range_quartile_current: The worker's current salary position within the salary range quartiles.
    salary_range_quartile_new: The proposed salary position within the salary range quartiles after change.
    base_salary_frequency: The frequency with which the base salary is paid (e.g., Bi-Weekly).
    salary_range_compa_ratio_current: The current comparison ratio of the worker’s salary to the midpoint of the range.
    salary_range_compa_ratio_new: The proposed new comparison ratio of the salary to the range midpoint.
    base_salary_new: The proposed new base salary for the worker.
    base_salary_currency: The currency in which the worker's base salary is paid.
    salary_range_position_current: The worker’s current position within the salary range.
    salary_range_position_new: The worker’s new position within the salary range.
    salary_range_midpoint_current: The current midpoint of the salary range for the worker's role.
    salary_range_decile_new: The proposed new decile of the worker’s salary range.
    annualized_full_time_salary_factor: A factor representing the worker’s status relative to full-time work.
    salary_range_decile_current: The worker’s current decile in the salary range.
    base_salary_change_amount: The amount of change in the base salary.
    salary_range_quintile_current: The current quintile in which the worker’s salary falls.
    prior_salary_change_date: The date on which the worker's salary was last changed.
    adjusted_salary_frequency: The frequency at which the adjusted salary is paid.
    prior_salary_change_amount: The amount of the previous salary change.
    adjusted_salary_factor: The factor applied to adjust the worker's salary.
    salary_range_quintile_new: The new quintile for the worker's salary after adjustment.
    prior_salary_change_percentage: The percentage of the previous salary change.
    proposed_assignment_name: The name of the proposed new assignment for the worker.
    promotion_effective_date: The date on which the worker’s promotion becomes effective.
    salary_range_high_new: The proposed new highest value in the salary range.
    salary_range_midpoint_new: The new midpoint of the salary range.
    salary_range_low_new: The proposed new lowest value in the salary range.
    promotion_fields_last_update_date: The last date when promotion-related fields were updated.
    promotion_fields_last_updated_by: The person or entity that last updated the promotion fields.
    promotion_fields_originally_updated_by: The original person or entity that updated the promotion fields.
    proposed_grade: The new grade proposed for the worker.
    proposed_grade_code: The code associated with the proposed new grade.
    proposed_job: The new job role proposed for the worker.
    proposed_job_code: The code associated with the proposed new job.
    proposed_position: The new position proposed for the worker.
    proposed_position_code: The code associated with the proposed position.
    grade_ladder: The career progression ladder for the worker's current grade.
    grade_step: The worker’s current step within their grade.
    proposed_grade_step: The proposed new step within the worker’s grade.
    compensation_performance_rating_current: The worker’s current compensation performance rating.
    performance_management_calculated_performance_goal_rating: The calculated rating for performance goals.
    performance_management_overall_performance_goal_rating: The overall rating for performance goals.
    calibration_status: The status indicating whether performance ratings have been calibrated.
    performance_management_overall_development_goal_rating: The overall rating for development goals.
    performance_management_calculated_development_goal_rating: The calculated rating for development goals.
    compensation_performance_rating_update_date: The date on which the compensation performance rating was last updated.
    compensation_performance_rating_updated_by: The person or entity that last updated the compensation performance rating.
    performance_management_calculated_competency_rating: The calculated rating for the worker's competencies.
    performance_management_calculated_overall_rating: The calculated overall performance rating.
    performance_management_overall_competency_rating: The overall rating for the worker's competencies.
    performance_management_overall_rating: The overall performance rating of the worker.
    performance_management_rating_date: The date on which the overall performance rating was recorded.
    original_compensation_performance_rating_updated_by: The original person who updated the compensation performance rating.
    performance_document: A document that contains the worker’s performance review.
    performance_history: A list of past performance reviews for the worker.
    compensation_performance_rating_prior: The worker's prior compensation performance rating.
    compensation_performance_rating_date_prior: The date of the prior compensation performance rating.
    ranking: The worker’s relative ranking within their team or company.
    risk_of_loss: The assessed risk of the worker leaving the company.
    full_ranking: The worker's overall ranking across the entire company.
    worker_potential: The assessed potential of the worker for growth or promotion.
    compensation_history: A list of the worker's previous compensation amounts.
    notes: Any additional notes regarding the worker.
    attachments: Files or documents attached to the worker’s record.
    absence_history: A list of the worker's previous absences.
    market_composites: Market data relevant to the worker's compensation or position.
    assignment_segments: Segments or components of the worker’s current assignment.
    ui_trigger_for_individual_worker: A flag indicating whether an individual UI action was triggered for the worker.
 
    
disciplinary_actions schema:
    - `person_name`: The name of the employee involved in the disciplinary action.
    - `action`: The type of disciplinary action taken (e.g., "Verbal Warning", "Written Warning").
    - `reason`: The reason for the disciplinary action (e.g., "Late submission of project reports").
    - `status`: The current status of the disciplinary action (e.g., "resolved", "pending").
    - `event_date`: The date of the incident or event that triggered the disciplinary action.
    - `action_date`: The date the disciplinary action was implemented.
    - `action_by`: The name of the person (e.g., manager, HR) who took the disciplinary action.
    - `severity`: The severity of the action (e.g., "minor", "major").
    - `manager_name`: The name of the manager responsible for handling the disciplinary action.
    
    - `followup_tasks`: A list of tasks assigned as follow-up actions related to the disciplinary event. For each task, the following fields are included:
        - `task_description`: A description of the follow-up task.
        - `due_date`: The date by which the follow-up task is due.
        - `status`: The current status of the task (e.g., "pending", "completed").
    
    - `appeal_status`: The status of the appeal, if any (e.g., "accepted", "rejected").
    - `acknowledged_at`: The date and time when the employee acknowledged the disciplinary action.
    - `created_at`: The timestamp when the disciplinary action was created (to track when the process was initiated).
    - `updated_at`: The timestamp when the disciplinary action was last updated (to track changes in status, comments, or follow-ups).
 
 
Instructions:
- Analyze the user's prompt and select the appropriate field names from the provided schemas.
- If the user request is ambiguous or general (e.g., "Turnover report"), infer the most relevant fields.
- Provide the field names as a Python dictionary with schema names as keys, and a list of relevant field names as values.
- Map synonyms and related terms used by the user to the correct field name. For example:
    - "compensation" refers to "base_salary" and "compensation" fields.
    - "department" refers to "organization_unit" and "business_unit."
    - "demographics" refers to fields like "date_of_birth", "gender", "nationality."
-Always include person_name for all schema.
- Always narrow down the selection to the minimum required fields based on the query.
- If the user asks for common HR reports (e.g., headcount, diversity, compensation analysis, turnover), include typical fields for those report types even if the user doesn't specify them.
 
input:{user_prompt}
response: Provide the fields as a Python dictionary with collection names and field lists.
"""
 
# Create a LangChain prompt template
prompt_template = PromptTemplate(input_variables=["user_prompt"], template=base_prompt)
 
# Function to get the raw response from the LLM
def get_raw_response(user_prompt):
    # Setup the LLMChain with the prompt template and the OpenAI model
    llm_chain = LLMChain(llm=OPENAI_LLM, prompt=prompt_template)
    
    # Run the chain and return the AI agent's raw response
    response = llm_chain.run({"user_prompt": user_prompt})
    return response
 
# Function to format the response into a dictionary with schema names
def format_response_as_dictionary(response):
    # Clean the response and convert it to a valid Python dictionary
    try:
        # Remove any extraneous text like ```python ... ```
        code_match = re.search(r"```python(.*?)```", response, re.DOTALL)
        if code_match:
            response = code_match.group(1).strip()  # Extract the inner code block
 
        # Use ast.literal_eval to safely evaluate the string as a Python dictionary
        fields_by_schema = ast.literal_eval(response)
        
        if isinstance(fields_by_schema, dict):
            print("Formatted response:", fields_by_schema)
            return fields_by_schema
        else:
            raise ValueError("Response is not a valid dictionary")
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing AI response: {e}")
        return {}
 
# Main function to generate and format report fields
def generate_graph_fields(user_prompt):
    # Get the raw response from the LLM
    raw_response = get_raw_response(user_prompt)
    print("*"*25)
    print("raw_response : ",raw_response)
    # Format the response into a dictionary
    formatted_response = format_response_as_dictionary(raw_response)
    
    return formatted_response

def generate_report3():
    # request_data = request.get_json()
    # report_name = request_data.get('report_name')
    # print("report name : ", report_name)
    # print("*" * 25)
    user_description = "Generate a Compa-Ratio Averages report, broken down by department, filtered for specific grades, covering the last 12 months."
 # User-provided description
 
    # Fetch the report info from the report_fields_mapping1
    report_info = generate_graph_fields(user_description)
    print(report_info)
    # Initialize full_data
    full_data = []
 
    # Fetch full data from all collections (without limiting to 50 employees)
    for idx, (collection_name, field_names) in enumerate(report_info.items()):
        projection = {field: 1 for field in field_names}
        projection.update({'_id': 0})
 
        # print("collection name : ", collection_name)
        # print("*" * 25)
        # Fetch full dataset from each collection
        collection_data = list(db[collection_name].find({}, projection).limit(50))
 
        # print('collection name : ', collection_data)
        # print("*" * 25)
        
        collection_data2 = list(db[collection_name].find({}, projection).limit(1500))
        print()
        if idx == 0:
            # Initialize full_data with the first collection
            full_data = collection_data
        else:
            # Merge this collection's data with the full_data based on 'person_name'
            collection_data_dict = {employee.get('person_name', 'Unknown'): employee for employee in collection_data}
 
            for employee in full_data:
                person_name = employee.get('person_name')
                if person_name and person_name in collection_data_dict:
                    # Merge fields from this collection's data into full_data
                    for key in field_names:
                        employee[key] = collection_data_dict[person_name].get(key, None)
 
        if idx == 0:
            # Initialize full_data with the first collection
            full_data2 = collection_data2
        else:
            # Merge this collection's data with the full_data based on 'person_name'
            collection_data_dict2 = {employee.get('person_name', 'Unknown'): employee for employee in collection_data2}
 
            for employee in full_data2:
                person_name = employee.get('person_name')
                if person_name and person_name in collection_data_dict2:
                    # Merge fields from this collection's data into full_data
                    for key in field_names:
                        employee[key] = collection_data_dict2[person_name].get(key, None)

    # Assuming full_data and full_data2 are variables containing your data

    # Open the file with utf-8 encoding
    with open("Full data(50).txt", "w", encoding="utf-8") as file:
        file.write(str(full_data) + "\n\n")  # Converting data to string and writing it

    with open("Full data.txt", "w", encoding="utf-8") as file:    
        file.write(str(full_data2) + "\n")

@app.route('/uno', methods=['POST'])
def trigger_task_deadline_alerts():
    try:
        generate_report3()
        return jsonify({"message": "Task deadline alerts sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 

if __name__ == '__main__':
    app.run(debug=True)
