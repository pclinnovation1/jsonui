# structure.py
class EligibilityCriteria:
    def __init__(self):
        self.criteria = {
            "Personal": {
                "Gender": " ",
                "Person Type": " ",
                "Disabled": " ",
                "Uses Tobacco": " ",
                "Service Areas": " ",
                "Home Location": " ",
                "Postal Code Ranges": " ",
                "Opted for Medicare": " ",
                "Leave of Absence": " ",
                "Termination Reason": " ",
                "Qualification": " ",
                "Competency": " ",
                "Marital Status": " ",
                "Religion": " "
            },
            "Employment": {
                "Assignment Status": " ",
                "Hourly or Salaried": " ",
                "Assignment Category": " ",
                "Grade": " ",
                "Job": " ",
                "Position": " ",
                "Payroll": " ",
                "Salary Basis": " ",
                "Department": " ",
                "Legal Entities": " ",
                "Performance Rating": " ",
                "Quartile in Range": " ",
                "Work Location": " ",
                "Range of Scheduled Hours": " ",
                "People Manager": " ",
                "Job Function": " ",
                "Job Family": " ",
                "Hire Date": " ",
                "Probation Period": " ",
                "Business Unit": " "
            },
            "Derived Factors": {
                "Age": " ",
                "Length of Service": " ",
                "Compensation": " ",
                "Hours Worked": " ",
                "Full-Time Equivalent": " ",
                "Combined Age and Length of Service": " "
            },
            "Other": {
                "Benefit Groups": " ",
                "Health Coverage Selected": " ",
                "Participation in Another Plan": " ",
                "Formula": " ",
                "User-Defined Criteria": " "
            },
            "Labor Relations": {
                "Bargaining Unit": " ",
                "Labor Union Member": " ",
                "Union": " ",
                "Collective Agreement": " "
            }
        }
    
    def get_criteria(self):
        return self.criteria
