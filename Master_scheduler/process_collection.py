import json
from pymongo import MongoClient

# Correct the data structure
data = [
  # {
  #   "Process Name": "Calculate Accruals and Balances",
  #   "Description": "Generates details and balances for accrual plan...",
  #   "Schedule": "",
  #   "SubmissionNotes": "",
  #   "NotifyMeWhenThisProcessEnds": "",
  #   "BasicOptions": {
  #     "EffectiveDate": "",
  #     "RunAsTest": "",
  #     "IncludeTraceStatementsInAuditLog": "",
  #     "IncrementEffectiveDate": "",
  #     "Plan Type": ""
  #   },
  #   "PopulationFilters": {
  #     "Person": "",
  #     "BusinessUnit": "",
  #     "LegalEmployer": "",
  #     "PersonSelectionRule": "",
  #     "Changes Since Last Run": "",
  #     "Payroll": "",
  #     "Legislative Data Group": "",
  #     "Payroll Relationship Group": "",
  #     "Absence Plan": "",
  #     "Repeating Period": ""
  #   },
  #   "ProcessOptions": {
  #     "Language": "",
  #     "Territory": "",
  #     "TimeZone": "",
  #     "NumberFormat": "",
  #     "TimeFormat": "",
  #     "DateFormat": "",
  #     "Currency": ""
  #   },
  #   "AdvancedOptions": {
  #     "Schedule": {
  #       "AsSoonAsPossible": "",
  #       "UsingASchedule": {
  #         "Frequency": {
  #           "Once": {
  #             "Start Date": ""
  #           },
  #           "Hourly/Minute": {
  #             "Start Date": "",
  #             "End Date": "",
  #             "Time Between Runs": ""
  #           },
  #           "Daily": {
  #             "Start Date": "",
  #             "End Date": "",
  #             "Days Between Runs": ""
  #           },
  #           "Weekly": {
  #             "Start Date": "",
  #             "End Date": "",
  #             "Weeks Between Runs": ""
  #           },
  #           "Monthly": {
  #             "Start Date": "",
  #             "End Date": "",
  #             "Repeat By day": {
  #               "Week of the Month": "",
  #               "Day of the Week": ""
  #             },
  #             "Repeat By date": {
  #               "Date": ""
  #             }
  #           },
  #           "Yearly": {
  #             "Start Date": "",
  #             "End Date": "",
  #             "Month": "",
  #             "Repeat By day": {
  #               "Week of the Month": "",
  #               "Day of the Week": ""
  #             },
  #             "Repeat By date": {
  #               "Date": ""
  #             }
  #           },
  #           "User-Defined": {
  #             "Add Time": ""
  #           },
  #           "Use a Saved ScheduleUse a Saved Schedule": {
  #             "Schedule Name": ""
  #           }
  #         }
  #       }
  #     }
  #   },
  #   "Notification": {
  #     "AddressType": "",
  #     "Condition": "",
  #     "Recipient": ""
  #   }
  # },
  # {
  #   "Process Name": "Evaluate Certification Updates",
  #   "Description": "Evaluates certification due dates and updates a...",
  #   "Schedule": "",
  #   "SubmissionNotes": "",
  #   "NotifyMeWhenThisProcessEnds": "",
  #   "BasicOptions": {
  #     "EffectiveDate": "",
  #     "RunAsTest": "",
  #     "IncludeTraceStatementsInAuditLog": "",
  #     "IncrementEffectiveDate": "",
  #     "Plan Type": ""
  #   },
  #   "PopulationFilters": {
  #     "Person": "",
  #     "BusinessUnit": "",
  #     "LegalEmployer": "",
  #     "Person Selection Rule": "",
  #     "Payroll": "",
  #     "Legislative Data Group": ""
  #   },
  #   "ProcessOptions": {
  #     "Language": "",
  #     "Territory": "",
  #     "TimeZone": "",
  #     "NumberFormat": "",
  #     "TimeFormat": "",
  #     "DateFormat": "",
  #     "Currency": ""
  #   },
  #   "AdvancedOptions": {
  #     "Schedule": {
  #       "AsSoonAsPossible": "",
  #       "UsingASchedule": {
  #         "Frequency": {
  #           "Once": {
  #             "Start Date": ""
  #           },
  #           "Hourly/Minute": {
  #             "Start Date": "",
  #             "End Date": "",
  #             "Time Between Runs": ""
  #           },
  #           "Daily": {
  #             "Start Date": "",
  #             "End Date": "",
  #             "Days Between Runs": ""
  #           },
  #           "Weekly": {
  #             "Start Date": "",
  #             "End Date": "",
  #             "Weeks Between Runs": ""
  #           },
  #           "Monthly": {
  #             "Start Date": "",
  #             "End Date": "",
  #             "Repeat By day": {
  #               "Week of the Month": "",
  #               "Day of the Week": ""
  #             },
  #             "Repeat By date": {
  #               "Date": ""
  #             }
  #           },
  #           "Yearly": {
  #             "Start Date": "",
  #             "End Date": "",
  #             "Month": "",
  #             "Repeat By day": {
  #               "Week of the Month": "",
  #               "Day of the Week": ""
  #             },
  #             "Repeat By date": {
  #               "Date": ""
  #             }
  #           },
  #           "User-Defined": {
  #             "Add Time": ""
  #           },
  #           "Use a Saved ScheduleUse a Saved Schedule": {
  #             "Schedule Name": ""
  #           }
  #         }
  #       }
  #     }
  #   },
  #   "Notification": {
  #     "AddressType": "",
  #     "Condition": "",
  #     "Recipient": ""
  #   }
  # },
  # {
  #   "Process Name": "Update Accrual Plan Enrollments",
  #   "Description": "Evaluates employee events for enrollment and te...",
  #   "Schedule": "",
  #   "SubmissionNotes": "",
  #   "NotifyMeWhenThisProcessEnds": "",
  #   "BasicOptions": {
  #     "EffectiveDate": "",
  #     "RunAsTest": "",
  #     "IncludeTraceStatementsInAuditLog": "",
  #     "IncrementEffectiveDate": "",
  #     "Plan Type": ""
  #   },
  #   "PopulationFilters": {
  #     "Person": "",
  #     "BusinessUnit": "",
  #     "LegalEmployer": "",
  #     "PersonSelectionRule": "",
  #     "AbsencePlan": "",
  #     "PlanCategory": "",
  #     "Payroll": "",
  #     "LegislativeDataGroup": ""
  #   },
  #   "ProcessOptions": {
  #     "Language": "",
  #     "Territory": "",
  #     "TimeZone": "",
  #     "NumberFormat": "",
  #     "TimeFormat": "",
  #     "DateFormat": "",
  #     "Currency": ""
  #   },
  #   "AdvancedOptions": {
  #     "Schedule": {
  #       "AsSoonAsPossible": "",
  #       "UsingASchedule": {
  #         "Frequency": {
  #           "Once": {
  #             "Start Date": ""
  #           },
  #           "Hourly/Minute": {
  #             "Start Date": "",
  #             "End Date": "",
  #             "Time Between Runs": ""
  #           },
  #           "Daily": {
  #             "Start Date": "",
  #             "End Date": "",
  #             "Days Between Runs": ""
  #           },
  #           "Weekly": {
  #             "Start Date": "",
  #             "End Date": "",
  #             "Weeks Between Runs": ""
  #           },
  #           "Monthly": {
  #             "Start Date": "",
  #             "End Date": "",
  #             "Repeat By day": {
  #               "Week of the Month": "",
  #               "Day of the Week": ""
  #             },
  #             "Repeat By date": {
  #               "Date": ""
  #             }
  #           },
  #           "Yearly": {
  #             "Start Date": "",
  #             "End Date": "",
  #             "Month": "",
  #             "Repeat By day": {
  #               "Week of the Month": "",
  #               "Day of the Week": ""
  #             },
  #             "Repeat By date": {
  #               "Date": ""
  #             }
  #           },
  #           "User-Defined": {
  #             "Add Time": ""
  #           },
  #           "Use a Saved ScheduleUse a Saved Schedule": {
  #             "Schedule Name": ""
  #           }
  #         }
  #       }
  #     }
  #   },
  #   "Notification": {
  #     "AddressType": "",
  #     "Condition": "",
  #     "Recipient": ""
  #   }
  # }

# {
#     "Process Name": "Learning Assignment",
#     "Description": "New Learning Assignment information for employee.",
#     "Schedule": "",
#     "SubmissionNotes": "",
#     "NotifyMeWhenThisProcessEnds": "",
#     "BasicOptions": {
#       "EffectiveDate": "",
#       "RunAsTest": "",
#       "IncludeTraceStatementsInAuditLog": "",
#       "IncrementEffectiveDate": "",
#       "Plan Type": ""
#     },
#     "PopulationFilters": {
#        "InitiativeName": "",
#        "InitiativeStatus": "",
#        "InitiativeType": "",
#        "InitiativeStartDate": "",
#        "InitiativeStopDate": "",
#        "OverdueAssignments": "",
#        "IncompleteAssignments": "",
#        "CompletedAssignments": "",
#        "LearnersWithPendingEvaluation": "",
#        "LastAssignedDate": "",
#        "PersonNumber": ""
#     },
#     "ProcessOptions": {
#       "Language": "",
#       "Territory": "",
#       "TimeZone": "",
#       "NumberFormat": "",
#       "TimeFormat": "",
#       "DateFormat": "",
#       "Currency": ""
#     },
#     "AdvancedOptions": {
#       "Schedule": {
#         "AsSoonAsPossible": "",
#         "UsingASchedule": {
#           "Frequency": {
#             "Once": {
#               "Start Date": ""
#             },
#             "Hourly/Minute": {
#               "Start Date": "",
#               "End Date": "",
#               "Time Between Runs": ""
#             },
#             "Daily": {
#               "Start Date": "",
#               "End Date": "",
#               "Days Between Runs": ""
#             },
#             "Weekly": {
#               "Start Date": "",
#               "End Date": "",
#               "Weeks Between Runs": ""
#             },
#             "Monthly": {
#               "Start Date": "",
#               "End Date": "",
#               "Repeat By day": {
#                 "Week of the Month": "",
#                 "Day of the Week": ""
#               },
#               "Repeat By date": {
#                 "Date": ""
#               }
#             },
#             "Yearly": {
#               "Start Date": "",
#               "End Date": "",
#               "Month": "",
#               "Repeat By day": {
#                 "Week of the Month": "",
#                 "Day of the Week": ""
#               },
#               "Repeat By date": {
#                 "Date": ""
#               }
#             },
#             "User-Defined": {
#               "Add Time": ""
#             },
#             "Use a Saved ScheduleUse a Saved Schedule": {
#               "Schedule Name": ""
#             }
#           }
#         }
#       }
#     },
#     "Notification": {
#       "AddressType": "",
#       "Condition": "",
#       "Recipient": ""
#     }
#   },
  
# {
#     "Process Name": "Course Renewl",
#     "Description": "New this is for renewal of the course if applicable.",
#     "Schedule": "",
#     "SubmissionNotes": "",
#     "NotifyMeWhenThisProcessEnds": "",
#     "BasicOptions": {
#       "EffectiveDate": "",
#       "RunAsTest": "",
#       "IncludeTraceStatementsInAuditLog": "",
#       "IncrementEffectiveDate": "",
#       "Plan Type": ""
#     },
#     "PopulationFilters": {
#         "InitialAssignmentStatus": "",
#         "LearningItemAsOfDate": "",
#         "ValidityPeriodStarts": "",
#         "ValidityPeriodExpires": "",
#         "ValidFor": "",
#         "RenewalOptions": "",
#         "RenewalPeriod": "",
#         "LearnerReconciliation": "",
#         "RunAs": ""
#     },
#     "ProcessOptions": {
#       "Language": "",
#       "Territory": "",
#       "TimeZone": "",
#       "NumberFormat": "",
#       "TimeFormat": "",
#       "DateFormat": "",
#       "Currency": ""
#     },
#     "AdvancedOptions": {
#       "Schedule": {
#         "AsSoonAsPossible": "",
#         "UsingASchedule": {
#           "Frequency": {
#             "Once": {
#               "Start Date": ""
#             },
#             "Hourly/Minute": {
#               "Start Date": "",
#               "End Date": "",
#               "Time Between Runs": ""
#             },
#             "Daily": {
#               "Start Date": "",
#               "End Date": "",
#               "Days Between Runs": ""
#             },
#             "Weekly": {
#               "Start Date": "",
#               "End Date": "",
#               "Weeks Between Runs": ""
#             },
#             "Monthly": {
#               "Start Date": "",
#               "End Date": "",
#               "Repeat By day": {
#                 "Week of the Month": "",
#                 "Day of the Week": ""
#               },
#               "Repeat By date": {
#                 "Date": ""
#               }
#             },
#             "Yearly": {
#               "Start Date": "",
#               "End Date": "",
#               "Month": "",
#               "Repeat By day": {
#                 "Week of the Month": "",
#                 "Day of the Week": ""
#               },
#               "Repeat By date": {
#                 "Date": ""
#               }
#             },
#             "User-Defined": {
#               "Add Time": ""
#             },
#             "Use a Saved ScheduleUse a Saved Schedule": {
#               "Schedule Name": ""
#             }
#           }
#         }
#       }
#     },
#     "Notification": {
#       "AddressType": "",
#       "Condition": "",
#       "Recipient": ""
#     }
#   }

# {
#     "ProcessName": "Letter Generation",
#     "Description": "New this is for genearating letters.",
#     "Schedule": "",
#     "SubmissionNotes": "",
#     "NotifyMeWhenThisProcessEnds": "",
#     "BasicOptions": {
#       "EffectiveDate": "",
#       "RunAsTest": "",
#       "IncludeTraceStatementsInAuditLog": "",
#       "IncrementEffectiveDate": "",
#       "Plan Type": ""
#     },
#     "PopulationFilters": {
#        "Candidate Name": "",
#                   "Job Title": "",
#                   "Hiring Manager": "",
#                   "Projected Start Date": "",
#                   "Work Location": "",
#                   "Department": "",
#                   "Business Unit": "",
#                   "Legal Employer": "",
#                   "Recruiter": ""
#     },
#     "ProcessOptions": {
#       "Language": "",
#       "Territory": "",
#       "TimeZone": "",
#       "NumberFormat": "",
#       "TimeFormat": "",
#       "DateFormat": "",
#       "Currency": ""
#     },
#     "AdvancedOptions": {
#       "Schedule": {
#         "AsSoonAsPossible": "",
#         "UsingASchedule": {
#           "Frequency": {
#             "Once": {
#               "Start Date": ""
#             },
#             "Hourly/Minute": {
#               "Start Date": "",
#               "End Date": "",
#               "Time Between Runs": ""
#             },
#             "Daily": {
#               "Start Date": "",
#               "End Date": "",
#               "Days Between Runs": ""
#             },
#             "Weekly": {
#               "Start Date": "",
#               "End Date": "",
#               "Weeks Between Runs": ""
#             },
#             "Monthly": {
#               "Start Date": "",
#               "End Date": "",
#               "Repeat By day": {
#                 "Week of the Month": "",
#                 "Day of the Week": ""
#               },
#               "Repeat By date": {
#                 "Date": ""
#               }
#             },
#             "Yearly": {
#               "Start Date": "",
#               "End Date": "",
#               "Month": "",
#               "Repeat By day": {
#                 "Week of the Month": "",
#                 "Day of the Week": ""
#               },
#               "Repeat By date": {
#                 "Date": ""
#               }
#             },
#             "User-Defined": {
#               "Add Time": ""
#             },
#             "Use a Saved ScheduleUse a Saved Schedule": {
#               "Schedule Name": ""
#             }
#           }
#         }
#       }
#     },
#     "Notification": {
#       "AddressType": "",
#       "Condition": "",
#       "Recipient": ""
#     }
#   }
{
  "Function Name": "Scheduled Processes for Performance Goals",
  "Process Name": "Scheduled Processes for Performance Goals",
  "AdvancedOptions": {
    "AsSoonAsPossible": "",
    "UsingASchedule": {
      "Frequency": {
        "Once": {
          "Start Date": ""
        },
        "HourlyMinute": {
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
        },
        "UserDefined": {
          "Add Time": ""
        },
        "Use A Saved Schedule": {
          "Schedule Name": ""
        }
      }
    }
  },
  "BasicOptions": {
    "EffectiveDate": "",
    "IncludeTraceStatementsInAuditLog": "",
    "IncrementEffectiveDate": "",
    "PlanType": "",
    "RunAsTest": ""
  },
  "Description": "Scheduling the processes for Performance",
  "Notification": {
    "AddressType": "",
    "Condition": "",
    "FunctionName": "Scheduled_Processes_for_Performance_Goals",
    "Recipient": ""
  },
  "NotifyMeWhenThisProcessEnds": "",
  "PopulationFilters": {
    "Process Type": "",
  "Process Name": "",
  "Goal Plan Start Date": "",
  "Goal Plan End Date": "",
  "Effective Date": ""
  
  },
  "ProcessOptions": {
    "Currency": "",
    "DateFormat": "",
    "Language": "",
    "NumberFormat": "",
    "Territory": "",
    "TimeFormat": "",
    "TimeZone": ""
  },
  "Schedule": "",
  "SubmissionNotes": ""

}
]


# Establish a connection to MongoDB
client = MongoClient("mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns")  # Change the connection string as needed
db = client["PCL_Interns"]  # Replace with your database name
collection = db["Processes_Collection2"]  # Replace with your collection name

# Insert the data into the collection
collection.insert_many(data)

print("Data inserted successfully.")
