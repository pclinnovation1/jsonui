# send_email.py
from config import app, db, mail
from flask_mail import Message
from flask import render_template_string

templates_collection = db['templates']

def send_email_notification(subject, recipient_name, recipient_email, company_email, event, dynamic_params={}, attachments=[]):
    # Fetch the template from MongoDB by event name
    template = templates_collection.find_one({'event': event})
    
    if template:
        body_template = template['body']
        # Render the template with dynamic parameters
        body = render_template_string(body_template, name=recipient_name, email=recipient_email, company_email=company_email, **dynamic_params)
        
        msg = Message(subject,
                      sender=company_email,
                      recipients=[recipient_email])
        msg.body = body
        
        for attachment in attachments:
            with app.open_resource(attachment['path']) as att:
                msg.attach(attachment['filename'], attachment['content_type'], att.read())
        
        with app.app_context():
            mail.send(msg)
    else:
        print(f"Template for event '{event}' not found.")

if __name__ == '__main__':
    # Example usage for leave approval
    subject = "Leave Approval Notification"
    recipient_name = "Jane Smith"
    recipient_email = "jane.smith@example.com"
    company_email = "info@company.com"
    event = 'leave_approval'  # Event name to find the template
    dynamic_params = {
        'start_date': "2023-07-01",
        'end_date': "2023-07-10"
    }
    attachments = [
        {
            'path': 'path/to/attachment1.pdf',
            'filename': 'attachment1.pdf',
            'content_type': 'application/pdf'
        }
    ]
    send_email_notification(subject, recipient_name, recipient_email, company_email, event, dynamic_params, attachments)
