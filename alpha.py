
from pymongo import MongoClient
import pprint

# MongoDB client setup (replace with actual connection details if different)
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
db = client['PCL_Interns']
employee_collection = db['s_employeedetails_1']

# Modified get_matching_employees function
def get_matching_employees(eligibility_profiles):
    matched_employees = set()
    for profile in eligibility_profiles:
        print("profile:, ", profile)
        print()
        criteria = profile["Create Participant Profile"]["Eligibility Criteria"]
        print("criteria:, ", criteria)
        print()
        query = {}

        # Construct query based on non-null criteria fields in Personal section
        personal_criteria = criteria.get("Personal", {})
        print("personal_criteria:, ", personal_criteria)
        print()
        for key, value in personal_criteria.items():
            if value and value.lower() not in ["n/a", "all"]:
                field_name = key.replace(' ', '_')
                query[field_name] = value

        # Construct query based on non-null criteria fields in Employment section
        employment_criteria = criteria.get("Employment", {})
        for key, value in employment_criteria.items():
            if value and value.lower() not in ["n/a", "all"]:
                field_name = key.replace(' ', '_')
                query[field_name] = value

        # Print the constructed query for debugging
        print(f"Constructed Query: {query}")
        print()

        employees = employee_collection.find(query)
        for employee in employees:
            matched_employees.add(employee["Person_Number"])

        # Print the matched employees for debugging
        print(f"Matched Employees for profile {profile['Create Participant Profile']['Eligibility Profile Definition']['Name']}: {list(matched_employees)}")

    return list(matched_employees)

# Mock eligibility profiles
eligibility_profiles = [
{
  "_id": {
    "$oid": "66718be302b341a4796cae3a"
  },
  "Create Participant Profile": {
    "Eligibility Profile Definition": {
      "Name": "Junior Staff Eligibility",
      "Profile Type": "Employee",
      "Profile Usage": "Performance Management",
      "Description": "Eligibility criteria for junior staff",
      "Assignment to Use": "Primary",
      "Status": "Active",
      "View Hierarchy": "Flat"
    },
    "Eligibility Criteria": {
      "Personal": {
        "Gender": "Male",
        "Person Type": "N/A",
        "Disabled": "N/A",
        "Uses Tobacco": "N/A",
        "Service Areas": "N/A",
        "Home Location": "N/A",
        "Postal Code Ranges": "N/A",
        "Opted for Medicare": "N/A",
        "Leave of Absence": "N/A",
        "Termination Reason": "N/A",
        "Qualification": "N/A",
        "Competency": "N/A",
        "Marital Status": "Married",
        "Religion": "N/A"
      },
      "Employment": {
        "Assignment Status": "N/A",
        "Hourly or Salaried": "N/A",
        "Assignment Category": "N/A",
        "Grade": "Junior",
        "Job": "N/A",
        "Position": "N/A",
        "Payroll": "N/A",
        "Salary Basis": "N/A",
        "Department": "N/A",
        "Legal Entities": "N/A",
        "Performance Rating": "N/A",
        "Quartile in Range": "N/A",
        "Work Location": "N/A",
        "Range of Scheduled Hours": "N/A",
        "People Manager": "N/A",
        "Job Function": "N/A",
        "Job Family": "N/A",
        "Hire Date": "N/A",
        "Probation Period": "N/A",
        "Business Unit": "N/A"
      },
      "Derived Factors": {
        "Age": "N/A",
        "Length of Service": "N/A",
        "Compensation": "N/A",
        "Hours Worked": "N/A",
        "Full-Time Equivalent": "N/A",
        "Combined Age and Length of Service": "N/A"
      },
      "Other": {
        "Benefit Groups": "N/A",
        "Health Coverage Selected": "N/A",
        "Participation in Another Plan": "N/A",
        "Formula": "N/A",
        "User-Defined Criteria": "N/A"
      },
      "Labor Relations": {
        "Bargaining Unit": "N/A",
        "Labor Union Member": "N/A",
        "Union": "N/A",
        "Collective Agreement": "N/A"
      }
    }
  }
}
]

# Function to test get_matching_employees
def test_get_matching_employees():
    matched_employees = get_matching_employees(eligibility_profiles)
    pprint.pprint(matched_employees)

# Run the test
if __name__ == "__main__":
    test_get_matching_employees()
