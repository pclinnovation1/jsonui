from flask import Flask, jsonify
from pymongo import MongoClient
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

# Flask App initialization
app = Flask(__name__)

# MongoDB connection setup
MONGODB_URI = config.MONGODB_URI
DATABASE_NAME = config.DATABASE_NAME

# Set up MongoDB client and database
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]


# MongoDB collections
my_goals_collection = db[config.COLLECTIONS["my_goals_collection"]]
employee_details_collection = db[config.COLLECTIONS["employee_details_collection"]] # Assumed employee details collection
email_template=db[config.COLLECTIONS["email_template"]]

# Fetch the email template from MongoDB collection
def get_email_template(template_name):
    template = email_template.find_one({"template_name": template_name})
    if not template:
        raise Exception(f"Template '{template_name}' not found.")
    return template

# Email sending function (using smtplib)
def send_email(email_data):
    try:
        # Set up the SMTP server
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(config.alert['from_email'], config.alert['ps'])  # Replace with your email and password

        # Create the email message
        msg = MIMEMultipart('alternative')
        msg['From'] = email_data['from_email']
        msg['To'] = email_data['to_email']
        msg['Subject'] = email_data['subject']  # Dynamic subject based on the alert type

        # Attach the HTML body content
        html_content = MIMEText(email_data['body'], 'html')  # Specify 'html' for HTML content
        msg.attach(html_content)

        # Send the email
        server.sendmail(email_data['from_email'], email_data['to_email'], msg.as_string())
        server.quit()
        print(f"Email sent to {email_data['to_email']}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

# Function to send goal alerts based on deadline proximity
def send_goal_deadline_alerts():
    current_date = datetime.now().date()

    # Fetch all goals from the collection
    goals = my_goals_collection.find()
    for goal in goals:
        alert_goals = []
        
        # Check if goal deadline is approaching
        goal_due_date = datetime.strptime(goal['target_completion_date'], '%Y-%m-%d').date()
        days_until_goal_due = (goal_due_date - current_date).days
        if (goal['progress'].lower() != 'completed') and any(days_until_goal_due == days for days in config.alert['goal_deadline_alert_days']):
            alert_goals.append({
                'task_name': goal['goal_name'],
                'due_date': goal['target_completion_date'],
                'days_left': days_until_goal_due
            })

        # Send email if there are approaching deadlines for goals
        if alert_goals:
            employee = employee_details_collection.find_one({'person_name': goal['person_name']})
            if employee:
                send_upcoming_deadline_email(goal['person_name'], employee.get('email', ''), alert_goals, alert_type="goal")

# Function to send task alerts based on deadline proximity
def send_task_deadline_alerts():
    current_date = datetime.now().date()

    # Fetch all goals from the collection
    goals = my_goals_collection.find()
    for goal in goals:
        alert_tasks = []

        # Check tasks within the goal if their deadline is approaching
        for task in goal.get('tasks', []):
            task_due_date = datetime.strptime(task['target_completion_date'], '%Y-%m-%d').date()
            days_until_task_due = (task_due_date - current_date).days
            if (task['status'].lower() != 'completed') and any(days_until_task_due == days for days in config.alert['task_deadline_alert_days']):
                # Append task information along with the goal name
                alert_tasks.append({
                    'task_name': task['name'],
                    'goal_name': goal['goal_name'],  # Include goal name here
                    'due_date': task['target_completion_date'],
                    'days_left': days_until_task_due
                })

        # Send email if there are approaching deadlines for tasks
        if alert_tasks:
            employee = employee_details_collection.find_one({'person_name': goal['person_name']})
            if employee:
                send_upcoming_deadline_email(goal['person_name'], employee.get('email', ''), alert_tasks, alert_type="task")

# Helper function to send email alerts for upcoming deadlines using a template
def send_upcoming_deadline_email(person_name, email, alert_items, alert_type):
    if not email:
        print(f"No email found for {person_name}. Skipping notification.")
        return

    # Get the appropriate template based on alert_type
    if alert_type == "goal":
        template_name = "goal_deadline_template"  # Update with the actual template name in your collection
    else:
        template_name = "task_deadline_template"  # Update with the actual template name in your collection

    # Fetch email template from MongoDB
    template = get_email_template(template_name)

    # Replace placeholders in the template with actual values
    if alert_type == "goal":
        # For goal alerts
        item_list_html = "".join(
            f"<li>Goal: {item['task_name']} - Due by {item['due_date']} - {item['days_left']} days left</li>"
            for item in alert_items
        )
    else:
        # For task alerts, include both task name and goal name
        item_list_html = "".join(
            f"<li>Task: {item['task_name']} (Goal: {item['goal_name']}) - Due by {item['due_date']} - {item['days_left']} days left</li>"
            for item in alert_items
        )

    # Customize the email body using placeholders in the template
    body = template['body'].format(
        person_name=person_name,
        task_list=item_list_html,
        company_name=config.alert['company_name']
    )

    # Prepare email data with dynamic subject and body
    email_data = {
        "to_email": email,
        "from_email": ['from_email'],
        "subject": template['subject'],  # Use the subject from the template
        "body": body
    }

    # Send the email
    send_email(email_data)
    print(f"Upcoming {alert_type} deadline email sent to {person_name} at {email}")

# Flask route to trigger the goal deadline alerts
@app.route('/send-goal-deadline-alerts', methods=['POST'])
def trigger_goal_deadline_alerts():
    try:
        send_goal_deadline_alerts()
        return jsonify({"message": "Goal deadline alerts sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Flask route to trigger the task deadline alerts
@app.route('/send-task-deadline-alerts', methods=['POST'])
def trigger_task_deadline_alerts():
    try:
        send_task_deadline_alerts()
        return jsonify({"message": "Task deadline alerts sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
