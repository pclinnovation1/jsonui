import ast
import os
from pprint import pprint
import re
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate  # Correct import for PromptTemplate
from langchain.chains import LLMChain  # Correct import for LLMChain
# Suppress Deprecation Warnings
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
 
# Setup the OpenAI API key directly with ChatOpenAI
OPENAI_LLM = ChatOpenAI(model="gpt-4", temperature=0.0, openai_api_key="...")  # Replace with your actual API key
 
# Prompts Definition
base_prompt = """
You are an intelligent assistant responsible for analyzing user prompts and generating relevant field names for various HR reports. Your job is to understand the user's prompt and provide only the relevant field names from the schemas listed below.
 
Here are the available schemas and fields you can work with:
 
HRM_employee_details schema:
    person_number: Unique ID assigned to the employee.
    person_name: Full name of the employee.
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
    hire_date: The employee's hire date.
    termination_date: The employee's termination date.
    employment_type: Blue collar or white collar etc.(BC or WC)
    job_code: job of employees belongs to.
    worker_category: Blue collar or white collar etc.(BC or WC)
 
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
    salary_effective_date: The date the current salary took effect.
    currency: The currency in which the salary is paid.
    fte: Full-time equivalent value.

    
api_absences_data schema:
    personNumber: A unique identifier assigned to each employee within the organization.
    absenceType: The category or type of absence being recorded, such as sick leave, vacation, etc.
    employer: The name of the entity or division within the organization that the employee works for.
    absenceReason: The specific reason provided for the absence, such as illness, personal leave, or family emergency.
    absenceDispStatus: The display status of the absence, indicating its visibility or state in the system (e.g., visible, hidden).
    approvalStatusCd: A code that represents the approval status of the absence request (e.g., approved, pending, denied).
    processingStatus: Indicates the current processing state of the absence request (e.g., submitted, in review, processed).
    userMode: Describes how the record was accessed or modified, potentially differentiating between modes like 'user', 'admin', or 'system'    

PGM_goals schema:
    goal_id: Unique identifier for the goal.
    goal_name: Name or title of the goal.
    person_id: Unique identifier for the person assigned to the goal.
    person_number: Employee or person’s unique number in the system.
    assignment_id: Identifier for the goal’s assignment instance.
    description: Brief description or details about the goal.
    start_date: Date when the goal starts or becomes active.
    status: Current status of the goal (e.g., In Progress, Completed).
    target_completion_date: Intended date for goal completion.
    status_meaning: Descriptive meaning of the current status.
    percent_complete: Percentage indicating the progress of the goal.    

    
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