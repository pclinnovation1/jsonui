1. 
i)   http://127.0.0.1:5000/employment/view

{
  "person_name": "Laura Aho",
  "fields": ["all"]
}

or 

{
  "person_name": "Laura Aho",
  "fields": ["employment_status", "job_title", "department"]
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


3.   for probation periods
http://127.0.0.1:5000/probation/view

{
  "person_name": "Bernhard Ahrer"
}



4. 
  i)  http://127.0.0.1:5000/report/personal
  
  {
  "person_name": "Niko Ala-Pappila"
}


ii)   http://127.0.0.1:5000/report/compensation


{
  "person_name": "Niko Ala-Pappila"
}


5.
i) view
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
  "person_name": "Niko Ala-Pappila",
  "action": "Warning",
  "reason": "Late to work",
  "event_date": "2024-01-10T08:00:00Z",
  "action_date": "2024-01-15T08:00:00Z",
  "status": "active",
  "details": "Employee was late to work multiple times in the past month."
}



ii) view  http://127.0.0.1:5000/discipline/view

{
  "person_name": "Niko Ala-Pappila"
}

#to be done by manager or hr only
iii) update  http://127.0.0.1:5000/discipline/update

{
  "person_name": "Niko Ala-Pappila",
  "action": "Warning",
  "update_fields": {
    "reason": "Repeated lateness",
    "status": "inactive",
    "action_by": "New Manager Name"
  }
}


#to be done by manager or hr only
iv) delete  http://127.0.0.1:5000/discipline/delete

{
  "person_name": "Niko Ala-Pappila",
  "action": "Warning"
}

#to be done by manager or hr only
7. change_manager

http://127.0.0.1:5000//change_manager/update

{
  "employee_names": ["Sven Lechner", "John Doe1", "Jane Smith1"],
  "new_manager_name": "Kamil Barowski"
}







