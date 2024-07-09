from flask import Flask, jsonify, request, current_app
from flask_mail import Mail, Message
from bson.objectid import ObjectId
from dotenv import load_dotenv
import datetime
from pymongo import MongoClient, DESCENDING
import os
from sender_email_config import EMAIL_CONFIGS, SMTP_SERVER, SMTP_PORT, USE_TLS

# MongoDB configuration
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
db = client['PCL_Interns']

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize Flask-Mail dynamically
def create_mail_instance(from_email):
    config = EMAIL_CONFIGS.get(from_email)
    if not config:
        raise ValueError(f"Email configuration not found for {from_email}")

    app = current_app._get_current_object()
    app.config.update(
        MAIL_SERVER=SMTP_SERVER,
        MAIL_PORT=SMTP_PORT,
        MAIL_USE_TLS=USE_TLS,
        MAIL_USERNAME=config['username'],
        MAIL_PASSWORD=config['password']
    )
    mail = Mail(app)
    return mail

# used to generate a entry in the email queue
def queue_email(data):
    email_data = {
        "to_email": data['to_email'],
        "from_email": data['from_email'],
        "subject": data['subject'],
        "template_name": data['template_name'],
        "created_at": datetime.datetime.utcnow(),
        "status": "pending",
        "data": data['data'],
        "attachments": data.get('attachments', [])
    }
    result = db['SCH_email_queue'].insert_one(email_data)
    if result.acknowledged:
        return {"message": "Email data inserted into the queue successfully", "id": str(result.inserted_id)}, True
    else:
        return {"message": "Failed to insert email data into the queue"}, False

# Fetch the email template from the database
def fetch_template(template_name):
    template_data = db['SCH_email_template'].find_one({"template_name": template_name})
    if not template_data:
        raise ValueError("Template not found")
    return template_data['body']

# Send emails from the queue
def send_emails():
    with app.app_context():
        pending_emails = db['SCH_email_queue'].find({"status": "pending"})
        send_successful = True
        for email in pending_emails:
            try:
                send_email(email)
                db['SCH_email_queue'].update_one(
                    {"_id": email['_id']},
                    {"$set": {"status": "sent", "sent_at": datetime.datetime.utcnow()}}
                )
                print(f"Successfully sent email to {email['to_email']}")
            except Exception as e:
                print(f"Failed to send email to {email['to_email']}: {str(e)}")
                db['SCH_email_queue'].update_one(
                    {"_id": email['_id']},
                    {"$set": {"status": "failed", "error_message": str(e)}}
                )
                send_successful = False
        return 'Completed' if send_successful else 'Partial Failure'

# Send the email for a given email data
def send_email(email):
    template_content = fetch_template(email['template_name'])
    
    # Create mail instance based on the from_email
    mail = create_mail_instance(email['from_email'])

    msg = Message(email['subject'], sender=email['from_email'], recipients=[email['to_email']])
    
    # Format the template with the provided data
    body = template_content.format(**email['data'])
    msg.body = body
    msg.html = body  # Set the HTML content of the email
    
    mail.send(msg)

# `queue_email_endpoint` is a POST endpoint that accepts a JSON payload with the following fields:
@app.route('/queue_email', methods=['POST'])
def queue_email_endpoint():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        result, success = queue_email(data)
        if not success:
            return jsonify({"error": result['message']}), 400
        return jsonify({"message": "Email data inserted into the queue successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# `send_email_now` is a POST endpoint that sends all pending emails in the queue.
@app.route('/send_email_now', methods=['POST'])
def send_email_now():
    status = send_emails()
    return status

if __name__ == '__main__':
    app.run(debug=True)
