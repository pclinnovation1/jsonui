import json
from pymongo import MongoClient
 
# Correct the data structure
data = [{
   "Process Name": "Update Accrual Plan Enrollments",
  "Description": "Evaluates employee events for enrollment and te...",
  "Schedule": "",
  "SubmissionNotes": "",
  "NotifyMeWhenThisProcessEnds": "",
  "BasicOptions": {
    "EffectiveDate": "",
    "RunAsTest": "",
    "IncludeTraceStatementsInAuditLog": "",
    "IncrementEffectiveDate": "",
    "Plan Type": ""
  },
  "PopulationFilters": {
    "Person": "",
    "BusinessUnit": "",
    "LegalEmployer": "",
    "PersonSelectionRule": "",
    "AbsencePlan": "",
    "PlanCategory": "",
    "Payroll": "",
    "LegislativeDataGroup": ""
  },
  "ProcessOptions": {
    "Language": "",
    "Territory": "",
    "TimeZone": "",
    "NumberFormat": "",
    "TimeFormat": "",
    "DateFormat": "",
    "Currency": ""
  },
  "AdvancedOptions": {
    "Schedule": {
      "AsSoonAsPossible": "",
      "UsingASchedule": {
        "Frequency": {
          "Once": {
            "Start Date": ""
          },
          "Hourly/Minute": {
            "Start Date": "",
            "End Date": "",
            "Time Between Runs": ""
          },
          "Daily": {
            "Start Date": "",
            "End Date": "",
            "Days Between Runs": ""
          },
          "Weekly": {
            "Start Date": "",
            "End Date": "",
            "Weeks Between Runs": ""
          },
          "Monthly": {
            "Start Date": "",
            "End Date": "",
            "Repeat By day": {
              "Week of the Month": "",
              "Day of the Week": ""
            },
            "Repeat By date": {
              "Date": ""
            }
          },
          "Yearly": {
            "Start Date": "",
            "End Date": "",
            "Month": "",
            "Repeat By day": {
              "Week of the Month": "",
              "Day of the Week": ""
            },
            "Repeat By date": {
              "Date": ""
            }
          }
        }
      }
    },
    "User-Defined": {
      "Add Time": ""
    },
    "Use a Saved ScheduleUse a Saved Schedule": {
      "Schedule Name": ""
    },
    "Notification": {
      "AddressType": "",
      "Condition": "",
      "Recipient": ""
    }
  },
  "Function Name": "generate_notifications"
  
}


]  

client = MongoClient("mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns")  # Change the connection string as needed
db = client["PCL_Interns"]  # Replace with your database name
collection = db["Processes_Collection2"]  # Replace with your collection name
 
# Insert the data into the collection
collection.insert_many(data)
 
print("Data inserted successfully.")