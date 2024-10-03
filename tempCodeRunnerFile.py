from flask import Flask, jsonify, request
from flask_mail import Mail, Message
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from general_algo import get_database

app = Flask(__name__)

# Configuration for Flask-Mail
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
USE_TLS = True

app.config.update(
    MAIL_SERVER=SMTP_SERVER,
    MAIL_PORT=SMTP_PORT,
    MAIL_USE_TLS=USE_TLS,
    MAIL_USERNAME="piyushbirkh@gmail.com",
    MAIL_PASSWORD="teaz yfbj jcie twrt"
)

mail = Mail(app)
db = None



# Function to add email data to the queue
def queue_email(data):
    try:
        email_data = {
            "to_email": data['to_email'],
            "from_email": data['from_email'],
            "template_name": data['template_name'],
            "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "status": "pending",
            "data": data['data'],
            "attachments": data.get('attachments', [])
        }
        db = get_database()
        result = db['SCH_email_queue'].insert_one(email_data)
        if result.acknowledged:
            print("Email data inserted into the queue successfully with ID:", result.inserted_id)
            return {"message": "Email data inserted into the queue successfully", "id": str(result.inserted_id)}, True
        else:
            print("Failed to insert email data into the queue")
            return {"message": "Failed to insert email data into the queue"}, False
    except Exception as e:
        print("Exception in queue_email:", str(e))
        return {"message": "Exception occurred while inserting email data into the queue"}, False

# Fetch the email template from the database
def fetch_template(template_name):
    db = get_database()
    template_data = db['SCH_email_template'].find_one({"template_name": template_name})
    if not template_data:
        raise ValueError("Template not found")
    return template_data['body'], template_data.get('subject', 'No Subject')

# Route to send an email
@app.route('/send_email', methods=['POST'])
def send_email_route():
    data = request.json
    if not data:
        return jsonify({"error": "Email data is required"}), 400
    try:
        send_email(data)
        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Function to send email
def send_email(email):
    template_content, subject = fetch_template(email['template_name'])
    msg = Message(subject, sender=email['from_email'], recipients=[email['to_email']])
    
    # Format the template with the provided data
    body = template_content.format(**email['data'])
    msg.body = body
    msg.html = body  # Set the HTML content of the email
    with app.app_context():
        mail.send(msg)

# Route to insert or update an email template
@app.route('/insert_template', methods=['POST'])
def insert_template():
    template_name = request.json.get('template_name')
    template_content = request.json.get('body')
    subject = request.json.get('subject')
    if not template_name or not template_content or not subject:
        return jsonify({"error": "Template name, subject, and content are required"}), 400

    db = get_database()
    result = db['SCH_email_template'].update_one(
        {"template_name": template_name},
        {"$set": {"body": template_content, "subject": subject}},
        upsert=True
    )

    if result.matched_count > 0:
        return jsonify({"message": "Template updated successfully"}), 200
    else:
        return jsonify({"message": "Template inserted successfully"}), 201

# Main entry point
if __name__ == '__main__':
    app.run(debug=True)
