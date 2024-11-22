1. 
  # for employee or Hr or Manager
i)   http://127.0.0.1:5000/employment/view

input:
{
  "person_name": "Laura Aho",
  "fields": ["all"]
}

or 

{
  "person_name": "Laura Aho",
  "fields": ["employment_status", "job_title", "department"]
}

output:
  {
    "allowance": 0,
    "base_salary": 2249.74,
    "benefits": 0,
    "department": "Manufacturing - chrome plating",
    "effective_end_date": "Thu, 01 Jan 1970 00:00:00 GMT",
    "effective_start_date": "Fri, 01 Sep 2017 00:00:00 GMT",
    "employment_country": "Finland",
    "employment_health_examination": "Thu, 10 Aug 2017 00:00:00 GMT",
    "employment_status": "Active",
    "employment_type": "Blue-collar",
    "fte": 1,
    "full_time_or_part_time": "Full time",
    "job_code": "TVR3",
    "job_family": "Chrome plating",
    "job_title": "",
    "latest_periodic_health_examination": "Thu, 01 Jan 1970 00:00:00 GMT",
    "legal_entity": "Oras Oy",
    "location": "Rauma",
    "manager_name": "Heinonen, Noora",
    "manager_person_number": 100113,
    "organization_number": "FI1315136",
    "organization_unit": "SURFACE TREATMENT",
    "overall_salary_per_month": 2249.74,
    "regular_or_temporary": "Regular",
    "role": "",
    "roles_list": "Employee",
    "salary_basis": "Monthly",
    "salary_class": "C3",
    "salary_effective_date": "Thu, 01 Feb 2024 00:00:00 GMT",
    "worker_category": "BC",
    "working_hours_per_week": 40,
    "working_hours_type": ""
}
  
  or
  
  {
    "department": "Manufacturing - chrome plating",
    "employment_status": "Active",
    "job_title": ""
}
  


#to be done by manager or hr only
ii)  http://127.0.0.1:5000/employment/update

  {
  "person_name": "Niko Ala-Pappila",
  "update_fields": {
    "department": "New Department",
    "job_title": "New Job Title"
  }
}

#to be done by manager or hr only
iii)  http://127.0.0.1:5000/employment/delete

   {
  "person_name": "Niko Ala-Pappila",
  "fields": ["all"]
}


or 


{
  "person_name": "Niko Ala-Pappila",
  "fields": ["department", "job_title"]
}


2. 
    http://127.0.0.1:5000/person_info/view
    
    {
  "person_name": "Mika Aalto",
  "fields": ["all"]
}

or

{
  "person_name": "Mika Aalto",
  "fields": ["email", "home_phone_number", "home_street_address"]
}


#to be done by manager or hr only
ii)   http://127.0.0.1:5000/person_info/update


{
  "person_name": "Mika Aalto",
  "update_fields": {
    "email": "new.email@orasgroup.com",
    "home_phone_number": "358123456789"
  }
}


#to be done by manager or hr only
iii)  http://127.0.0.1:5000/person_info/delete

{
  "person_name": "Mika Aalto",
  "fields": ["all"]
}

or

{
  "person_name": "Mika Aalto",
  "fields": ["home_phone_number", "home_email"]
}


3.
# for employee or hr or employee
for probation periods
input:
http://127.0.0.1:5000/probation/view

{
  "person_name": "Bernhard Ahrer"
}

output:
  {
    "trial_period": "6 months",
    "trial_period_ends": "Sat, 31 Dec 2022 00:00:00 GMT"
}
  

4. 
  i) # for employee or hr or manager
  http://127.0.0.1:5000/report/personal
  
  input:
  {
  "person_name": "Niko Ala-Pappila"
}
  output:
    {
    "birth_name": "Ala-Pappila",
    "date_of_birth": "Thu, 23 Mar 1989 00:00:00 GMT",
    "email": "niko.ala-pappila@orasgroup.com",
    "emergency_email": "",
    "emergency_name": "Teija Ala-Pappila",
    "emergency_phone": 358503680830,
    "first_name": "Niko",
    "gender": "Male",
    "given_name": "Niko",
    "home_city": "Rauma",
    "home_country": "Finland",
    "home_district": "",
    "home_email": "nikoap@windowslive.com",
    "home_phone_number": 358449653210,
    "home_postal_code": 26660,
    "home_regin": "",
    "home_state": "",
    "home_street_address": "Karpalopolku 4 as 5",
    "last_name": "Ala-Pappila",
    "manager_name": "Aaltonen, Katja",
    "manager_person_number": 100466,
    "nationality": "Finland",
    "person_name": "Niko Ala-Pappila",
    "person_number": 100471,
    "person_type": "Oras Group Employee",
    "place_of_birth": "",
    "username": "niko.ala-pappila@orasgroup.com"
}


ii) # for employee or hr or manager
http://127.0.0.1:5000/report/compensation

input:
{
  "person_name": "Niko Ala-Pappila"
}
output:
  {
    "allowance": 0,
    "bank_account": "FI1616273500016105",
    "base_salary": 2141.6,
    "benefits": 0,
    "cost_center_code": "NaN",
    "currency": "EUR",
    "overall_salary_per_month": 2141.6,
    "salary_basis": "Monthly",
    "salary_class": "C3",
    "salary_effective_date": "Thu, 01 Feb 2024 00:00:00 GMT",
    "salary_reason": "",
    "tax_number": NaN
}

5.
i)# for employee or hr or manager
view
http://127.0.0.1:5000/organizational_chart/view

for manual levels 

{
  "person_name": "Mauri Salovaara",
  "levels_above": 8,
  "levels_below": 3
}

or by default all level for above and below

{
  "person_name": "Mauri Salovaara"
}



#to be done by manager or hr only
6. 
i) add   http://127.0.0.1:5000/discipline/add

action_by filled by manually

{
  "person_name": "Niko Ala-Pappila",
  "action": "Warning",
  "reason": "Late to work",
  "event_date": "2024-01-10T08:00:00Z",
  "action_date": "2024-01-15T08:00:00Z",
  "action_by": "Manager Name",
  "status": "active",
  "details": "Employee was late to work multiple times in the past month."
}

if action_by is not provided in input (by default action_by)

{
    "person_name": "John Doe",
    "action": "Late to work",
    "reason": "Arrived late 3 times",
    "event_date": "2024-08-10",
    "action_date": "2024-08-11",
    "status": "active",
    "details": "Employee was late three times in a row."
}




ii) view  # to be done by hr or manager or employee
http://127.0.0.1:5000/discipline/view

input:
{
  "person_name": "Niko Ala-Pappila"
}

output:
  [
    {
        "_id": "66b208daf4306c3558a14d37",
        "action": "Warning",
        "action_by": "Manager Name",
        "action_date": "2024-01-15T08:00:00Z",
        "created_at": "2024-08-06T11:42:41.763235",
        "details": "Employee was late to work multiple times in the past month.",
        "employee_comments": [
            "I apologize and will improve."
        ],
        "event_date": "2024-01-10T08:00:00Z",
        "manager_comments": [
            "Please ensure punctuality."
        ],
        "person_name": "Niko Ala-Pappila",
        "reason": "Late to work",
        "status": "active"
    },
    {
        "_id": "66b2092af4306c3558a14d38",
        "action": "Warning",
        "action_by": "Aaltonen, Katja",
        "action_date": "2024-01-15T08:00:00Z",
        "created_at": "2024-08-06T11:29:46.049684",
        "details": "Employee was late to work multiple times in the past month.",
        "employee_comments": [],
        "event_date": "2024-01-10T08:00:00Z",
        "manager_comments": [],
        "person_name": "Niko Ala-Pappila",
        "reason": "Not completed assingment",
        "status": "active"
    }
]
  


iii) update   #to be done by manager or hr only
http://127.0.0.1:5000/discipline/update
{
  "person_name": "Niko Ala-Pappila",
  "reason": "Repeated lateness",
  "update_fields": {
    "action": "Warning",
    "status": "inactive",
    "action_by": "New Manager Name"
  }
}



iv) delete   #to be done by manager or hr only
http://127.0.0.1:5000/discipline/delete
{
  "person_name": "Niko Ala-Pappila",
  "reason": "Repeated lateness",
}

v) comment_manager  # for manager only
http://127.0.0.1:5000/discipline/comment/manager
input:
{
    "person_name": "Niko Ala-Pappila",
    "action": "Warning",
    "reason": "Late to work",
    "manager_comment": "Please ensure punctuality."
}


vi) comment_employee # for employee only

http://127.0.0.1:5000/discipline/comment/person
input:
{
    "person_name": "Niko Ala-Pappila",
    "action": "Warning",
    "reason": "Late to work",
    "employee_comment": "I apologize and will improve."
}


#to be done by manager or hr only
7. change_manager

http://127.0.0.1:5000//change_manager/update

{
  "employee_names": ["Sven Lechner", "John Doe1", "Jane Smith1"],
  "new_manager_name": "Kamil Barowski"
}



8. 
i) upload 
URL: http://127.0.0.1:5000/document/upload
Method: POST
Body: Form-data

file: <Select a file>
person_name: John Doe
uploaded_at: 2024-08-10T12:00:00Z


ii)  Get Employee
URL: http://127.0.0.1:5000/document/get_employee
Method: POST
Body: JSON

{
  "person_name": "John Doe"
}

iii)  Get Employee File
URL: http://127.0.0.1:5000/document/get_employee_file
Method: POST
Body: JSON

{
  "person_name": "John Doe",
  "filename": "Goals.docx"
}


iv) Delete Employee File
URL: http://127.0.0.1:5000/document/delete_employee_file
Method: POST
Body: JSON

{
  "person_name": "John Doe",
  "filename": "Goals.docx"
}


v) Delete Employee
URL: http://127.0.0.1:5000/document/delete_employee
Method: POST
Body: JSON

{
  "person_name": "John Doe"
}


9.
i) 
# by HR only
http://127.0.0.1:5000/policy/add_policy
input:
{
  "policy_name": "Code of Conduct8",
  "policy_text": "Detailed text of the Code of Conduct policy.",
  "policy_description": "This policy outlines the expected conduct for all employees.",
  "policy_type": "General Employment Policies",
  "effective_start_date": "2024-08-01",
  "effective_end_date": "2025-08-01",
  "attachments": ["Code_of_Conduct.pdf"],
  "reviewer_comments": "Reviewed and approved by Legal Department.",
  "approval_status": "Pending",
  "approval_date": "2024-07-15",
  "publication_date": "2024-07-16",
  "audience": ["Product","Finance"]
}


output:
{
  "policy_name": "Code of Conduct8",
  "policy_text": "Detailed text of the Code of Conduct policy.",
  "policy_description": "This policy outlines the expected conduct for all employees.",
  "policy_type": "General Employment Policies",
  "effective_start_date": "2024-08-01",
  "effective_end_date": "2025-08-01",
  "attachments": [
    "Code_of_Conduct.pdf"
  ],
  "reviewer_comments": "Reviewed and approved by Legal Department.",
  "approval_status": "Pending",
  "approval_date": "2024-07-15",
  "publication_date": "2024-07-16",
  "audience": [
    "product",
    "Finance"
  ],
  "update_history": []
}



# by HR only
http://127.0.0.1:5000/policy/update_policy
input:
{
  "policy_name": "Code of Conduct",
  "policy_text": "Updated text of the Code of Conduct policy.",
  "update_description": "Added new guidelines for remote work.",
  "updated_by": "HR Manager"
}
output:
{
  "policy_name": "Code of Conduct8",
  "policy_text": "Updated text of the Code of Conduct policy.",
  "policy_description": "This policy outlines the expected conduct for all employees.",
  "policy_type": "General Employment Policies",
  "effective_start_date": "2024-08-01",
  "effective_end_date": "2025-08-01",
  "attachments": [
    "Code_of_Conduct.pdf"
  ],
  "reviewer_comments": "Reviewed and approved by Legal Department.",
  "approval_status": "Pending",
  "approval_date": "2024-07-15",
  "publication_date": "2024-07-16",
  "audience": [
    "product",
    "Finance"
  ],
  "update_history": [
    {
      "update_description": "Updated policy fields",
      "updated_by": "HR Manager",
      "updated_date": "2024-08-07T16:06:52.327911",
      "old_values": {
        "policy_text": "Detailed text of the Code of Conduct policy."
      }
    }
  ]
}



http://127.0.0.1:5000/policy/acknowledge_policy
input:
{
  "policy_name": "Code of Conduct8",
  "person_name": "Mika Aalto",
  "acknowledgment_date": "2024-08-01",
  "comments": "Acknowledged the policy."
}
output:
{
  "policy_name": "Code of Conduct8",
  "person_name": "Mika Aalto",
  "person_number": "FI662",
  "acknowledgment_date": "2024-08-01",
  "comments": "Acknowledged the policy."
}

# by employee or hr or manager
http://127.0.0.1:5000/policy/view_policies
input:
{
  "policy_name": "Code of Conduct8"
}
output:
{
    "policies": [
        {
            "attachments": [
                "Code_of_Conduct.pdf"
            ],
            "audience": [
                "product",
                "Finance"
            ],
            "effective_end_date": "2025-08-01",
            "effective_start_date": "2024-08-01",
            "policy_description": "This policy outlines the expected conduct for all employees.",
            "policy_name": "Code of Conduct8",
            "policy_text": "Updated text of the Code of Conduct policy.",
            "policy_type": "General Employment Policies"
        }
    ]
}


input:
{
  "policy_type": "General Employment Policies"
}
output:
{
    "policies": [
        {
            "attachments": [
                "Code_of_Conduct.pdf"
            ],
            "audience": [
                "product",
                "Finance"
            ],
            "effective_end_date": "2025-08-01",
            "effective_start_date": "2024-08-01",
            "policy_description": "This policy outlines the expected conduct for all employees.",
            "policy_name": "Code of Conduct8",
            "policy_text": "Updated text of the Code of Conduct policy.",
            "policy_type": "General Employment Policies"
        }
    ]
}


input:
{
  "audience": "Product"
}
output:
{
    "policies": [
        {
            "attachments": [
                "Code_of_Conduct.pdf"
            ],
            "audience": [
                "Product",
                "Finance"
            ],
            "effective_end_date": "2025-08-01",
            "effective_start_date": "2024-08-01",
            "policy_description": "This policy outlines the expected conduct for all employees.",
            "policy_name": "Code of Conduct8",
            "policy_text": "Updated text of the Code of Conduct policy.",
            "policy_type": "General Employment Policies"
        }
    ]
}


10.
# for HR only
i) http://localhost:5000/salary/create_salary
input:
  {
    "person_name": "Jenni Aalto",
    "month": "January",
    "year": "2021",
    "basic": 9000,
    "hra": 5000,
    "special_allowance": 7000,
    "gross_earnings": 21000,
    "pf": 1196,
    "professional_tax": 200,
    "income_tax": 200,
    "total_deductions": 1596,
    "net_pay": 19404
}

output:
{
  "person_name": "Jenni Aalto",
  "month_year": "January 2021",
  "basic": 9000,
  "hra": 5000,
  "special_allowance": 7000,
  "gross_earnings": 21000,
  "pf": 1196,
  "professional_tax": 200,
  "income_tax": 200,
  "total_deductions": 1596,
  "net_pay": 19404
}

ii) # for HR only
http://localhost:5000/salary/update_salary
input:
{
    "person_name": "Ajay Kumar",
    "month": "January",
    "year": "2021",
    "basic": 9500,
    "hra": 5200
}

iii) # for HR only
http://localhost:5000/salary/delete_salary

input:
  {
    "person_name": "Ajay Kumar",
    "month": "January",
    "year": "2021"
}



11.
i) for employee
http://localhost:5000/payslip/download_payslip

input:
{
    "person_name": "Jenni Aalto",
    "month": "January",
    "year": "2021"
}



12.














