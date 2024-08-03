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

ii)  http://127.0.0.1:5000/employment/update

  {
  "person_name": "Niko Ala-Pappila",
  "update_fields": {
    "department": "New Department",
    "job_title": "New Job Title"
  }
}


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


ii)   http://127.0.0.1:5000/person_info/update


{
  "person_name": "Mika Aalto",
  "update_fields": {
    "email": "new.email@orasgroup.com",
    "home_phone_number": "358123456789"
  }
}


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

{
  "person_name": "Niko Ala-Pappila",
  "fields": ["all"]
}

or

{
  "person_name": "Niko Ala-Pappila",
  "fields": ["department", "job_title", "manager_name"]
}


ii)  update

http://127.0.0.1:5000/organizational_chart/update

{
  "person_name": "Niko Ala-Pappila",
  "update_fields": {
    "department": "New Department",
    "job_title": "New Job Title"
  }
}


iii)  delete

http://127.0.0.1:5000/organizational_chart/delete

{
  "person_name": "Niko Ala-Pappila",
  "fields": ["all"]
}

or

{
  "person_name": "Niko Ala-Pappila",
  "fields": ["department", "job_title"]
}







