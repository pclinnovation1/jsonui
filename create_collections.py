from pymongo import MongoClient

# Replace the URI with your MongoDB deployment's connection string.
client = MongoClient("mongodb://localhost:27017/")

# Create a database
db = client["Goals_performance"]

# Data for My Goals Collection
my_goals = [
    {
        "Goal Name": "Increase Sales",
        "Goal Type": "Performance",
        "Description": "Increase sales by 10% in Q1",
        "Start Date": "2024-01-01",
        "End Date": "2024-03-31",
        "Status": "In Progress",
        "Progress": 50,
        "Priority": "High",
        "Attachments": "sales.pdf",
        "Comments": "On track to meet target"
    },
    {
        "Goal Name": "Learn Python",
        "Goal Type": "Development",
        "Description": "Complete Python certification course",
        "Start Date": "2024-01-15",
        "End Date": "2024-04-15",
        "Status": "Not Started",
        "Progress": 0,
        "Priority": "Medium",
        "Attachments": "",
        "Comments": "Starting next week"
    },
    {
        "Goal Name": "Improve Team Communication",
        "Goal Type": "Business",
        "Description": "Conduct monthly team meetings",
        "Start Date": "2024-01-01",
        "End Date": "2024-12-31",
        "Status": "In Progress",
        "Progress": 20,
        "Priority": "High",
        "Attachments": "",
        "Comments": "Meetings scheduled"
    }
]

# Data for Goal Plans Collection
goal_plans = [
    {
        "Plan Name": "Q1 2024 Goals",
        "Plan Period": "Q1 2024",
        "Goals": ["Increase Sales", "Learn Python"],
        "Weighting": [60, 40],
        "Status": "In Progress",
        "Comments": "On track, need to start Python"
    },
    {
        "Plan Name": "Annual 2024 Plan",
        "Plan Period": "2024",
        "Goals": ["Increase Sales", "Improve Team Communication"],
        "Weighting": [50, 50],
        "Status": "In Progress",
        "Comments": "Sales target is key priority"
    }
]

# Data for Performance Reviews Collection (Employee Perspective)
performance_reviews_employee = [
    {
        "Employee Name": "John Doe",
        "Review Period": "Q1 2024",
        "Goals Assessed": ["Increase Sales", "Learn Python"],
        "Self-Assessment": ["Sales target met halfway", "Python not yet started"],
        "Manager Assessment": ["On track for sales", "start Python soon"],
        "Overall Rating": 4,
        "Feedback": ["Doing well", "focus on Python"],
        "Development Recommendations": "Allocate more time for Python"
    }
]

# Data for Team Goals Collection
team_goals = [
    {
        "Employee Name": "Jane Smith",
        "Goal Name": "Customer Satisfaction",
        "Goal Type": "Performance",
        "Description": "Improve customer satisfaction scores by 20%",
        "Start Date": "2024-01-01",
        "End Date": "2024-06-30",
        "Status": "In Progress",
        "Progress": 30,
        "Priority": "High",
        "Comments": "Needs more follow-up"
    },
    {
        "Employee Name": "Bob Johnson",
        "Goal Name": "New Client Acquisition",
        "Goal Type": "Performance",
        "Description": "Acquire 5 new clients",
        "Start Date": "2024-01-01",
        "End Date": "2024-03-31",
        "Status": "In Progress",
        "Progress": 60,
        "Priority": "High",
        "Comments": "Good progress so far"
    }
]

# Data for Goal Plans Management Collection
goal_plans_management = [
    {
        "Plan Name": "Q1 Team Goals",
        "Plan Period": "Q1 2024",
        "Assigned Employees": ["Jane Smith", "Bob Johnson"],
        "Goals": ["Customer Satisfaction", "New Client Acquisition"],
        "Weighting": [50, 50],
        "Status": "In Progress",
        "Comments": "Overall progress is good"
    }
]

# Data for Performance Reviews Collection (Manager Perspective)
performance_reviews_manager = [
    {
        "Employee Name": "Jane Smith",
        "Review Period": "Q1 2024",
        "Goals Assessed": ["Customer Satisfaction"],
        "Self-Assessment": "Making steady progress",
        "Manager Assessment": "Needs to increase follow-up",
        "Overall Rating": 3,
        "Feedback": "Good progress, more follow-up",
        "Development Recommendations": "Focus on follow-up techniques"
    },
    {
        "Employee Name": "Bob Johnson",
        "Review Period": "Q1 2024",
        "Goals Assessed": ["New Client Acquisition"],
        "Self-Assessment": "On track",
        "Manager Assessment": "Excellent progress",
        "Overall Rating": 5,
        "Feedback": "Keep up the great work",
        "Development Recommendations": "Continue current approach"
    }
]

# Data for Reporting and Analytics Collection (Manager Perspective)
reporting_analytics_manager = [
    {
        "Report Name": "Q1 Goal Progress",
        "Report Type": "Progress",
        "Time Period": "Q1 2024",
        "Data Sources": ["Employee Goals", "Reviews"],
        "Metrics": ["Completion Rate", "Performance Ratings"],
        "Visualizations": ["Bar Charts", "Line Graphs"],
        "Comments": "Overall team progress is satisfactory"
    }
]

# Data for Organizational Goals Collection (HR Perspective)
organizational_goals = [
    {
        "Goal Name": "Increase Market Share",
        "Goal Type": "Strategic",
        "Description": "Increase market share by 5%",
        "Start Date": "2024-01-01",
        "End Date": "2024-12-31",
        "Status": "In Progress",
        "Progress": 25,
        "Priority": "High",
        "Attachments": "market.pdf",
        "Comments": "Focus on marketing campaigns"
    }
]

# Data for Goal Plans Administration Collection (HR Perspective)
goal_plans_administration = [
    {
        "Plan Name": "Company-wide 2024 Plan",
        "Plan Period": "2024",
        "Goals": ["Increase Market Share", "Customer Satisfaction"],
        "Templates": "2024 Goals Template",
        "Assigned Departments": "All Departments",
        "Weighting": [60, 40],
        "Status": "In Progress",
        "Comments": "Aligning all departments"
    }
]

# Data for Performance Management Collection (HR Perspective)
performance_management = [
    {
        "Employee Name": "John Doe",
        "Review Period": "Q1 2024",
        "Goals Assessed": ["Increase Sales", "Learn Python"],
        "Self-Assessment": "Good progress on sales",
        "Manager Assessment": "Focus on completing Python",
        "Overall Rating": 4,
        "Feedback": "Doing well, focus on Python",
        "Development Recommendations": "Allocate more time for Python",
        "Compliance Checks": "Completed timely reviews"
    }
]

# Data for Analytics and Reporting Collection (HR Perspective)
analytics_reporting_hr = [
    {
        "Report Name": "Annual Performance",
        "Report Type": "Summary",
        "Time Period": "2024",
        "Data Sources": ["Performance Reviews", "Goals"],
        "Metrics": ["Overall Ratings", "Goal Achievements"],
        "Visualizations": ["Pie Charts", "Trend Lines"],
        "Comments": "Identified key performance areas"
    }
]

# Data for Training and Development Collection (HR Perspective)
training_development = [
    {
        "Program Name": "Leadership Training",
        "Description": "Training program for potential leaders",
        "Start Date": "2024-02-01",
        "End Date": "2024-06-01",
        "Participants": ["John Doe", "Jane Smith"],
        "Modules": ["Leadership Skills", "Team Management"],
        "Progress": 50,
        "Feedback": "Participants find it beneficial",
        "Development Goals": "Improve leadership capabilities"
    }
]

# Insert data into collections
db.my_goals.insert_many(my_goals)
db.goal_plans.insert_many(goal_plans)
db.performance_reviews_employee.insert_many(performance_reviews_employee)
db.team_goals.insert_many(team_goals)
db.goal_plans_management.insert_many(goal_plans_management)
db.performance_reviews_manager.insert_many(performance_reviews_manager)
db.reporting_analytics_manager.insert_many(reporting_analytics_manager)
db.organizational_goals.insert_many(organizational_goals)
db.goal_plans_administration.insert_many(goal_plans_administration)
db.performance_management.insert_many(performance_management)
db.analytics_reporting_hr.insert_many(analytics_reporting_hr)
db.training_development.insert_many(training_development)

print("Data inserted successfully")
