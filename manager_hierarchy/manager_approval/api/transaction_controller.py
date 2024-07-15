# from flask import Blueprint, request, jsonify, current_app, url_for
# from bson.objectid import ObjectId
# from datetime import datetime
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# transaction_bp = Blueprint('transaction_bp', __name__)

# @transaction_bp.route('/', methods=['POST'])
# def create_transaction():
#     data = request.get_json()
#     transaction = {
#         'employee_name': data['employee_name'],
#         'employee_id': data['employee_id'],
#         'conditions_statements': data['conditions_statements'],
#         'department': data['department'],
#         'global_status': 'pending',
#         'approvals': [],
#         'taken_actions': [],
#         'created_at': datetime.utcnow(),
#         'updated_at': datetime.utcnow()
#     }

#     managers = current_app.mongo.db.managers.find({"department": data['department']}).sort("level", 1)
#     for manager in managers:
#         transaction['approvals'].append({
#             "manager_name": manager['manager_name'],
#             "manager_level": manager['level'],
#             "email": manager['email'],
#             "local_status": "pending",
#             "reminder_sent": False
#         })

#     transaction_id = current_app.mongo.db.transactions.insert_one(transaction).inserted_id
#     transaction['_id'] = str(transaction_id)

#     # Send reminder to the level 1 manager
#     if transaction['approvals']:
#         first_approver = transaction['approvals'][0]
#         send_email_reminder(first_approver['email'], transaction, first_approver['manager_name'])

#     return jsonify({"message": "Transaction created", "transaction": transaction}), 201

# @transaction_bp.route('/reminders', methods=['POST'])
# def send_reminders():
#     data = request.get_json()
#     employee_id = data.get('employee_id')
    
#     if not employee_id:
#         return jsonify({"error": "'employee_id' is required."}), 400
    
#     transaction = current_app.mongo.db.transactions.find_one({"employee_id": employee_id, "global_status": "pending"})
    
#     if not transaction:
#         return jsonify({"error": "Transaction not found for the provided employee_id."}), 404
    
#     for approval in transaction['approvals']:
#         if approval['local_status'] == 'pending' and not approval['reminder_sent']:
#             approver = current_app.mongo.db.managers.find_one({"manager_name": approval['manager_name']})
#             if approver:
#                 send_email_reminder(approver['email'], transaction, approval['manager_name'])
#                 approval['reminder_sent'] = True
#                 current_app.mongo.db.transactions.update_one(
#                     {"_id": ObjectId(transaction['_id'])},
#                     {"$set": {"approvals": transaction['approvals']}}
#                 )
#             break
    
#     return jsonify({"message": "Reminders sent"}), 200

# def send_email_reminder(to_email, transaction, approver_name):
#     from_email = current_app.config['MAIL_USERNAME']
#     password = current_app.config['MAIL_PASSWORD']

#     # Debugging statements to ensure credentials are set
#     print(f"Sending email from: {from_email}")
#     print(f"Email password is set: {'Yes' if password else 'No'}")

#     if not from_email or not password:
#         raise ValueError("Email credentials are not set")

#     subject = "Approval Reminder"
#     approve_url = url_for('transaction_bp.update_approval_status', transaction_id=transaction['_id'], status='approved', approver_name=approver_name, _external=True)
#     reject_url = url_for('transaction_bp.update_approval_status', transaction_id=transaction['_id'], status='rejected', approver_name=approver_name, _external=True)
#     changes_url = url_for('transaction_bp.request_changes_form', transaction_id=transaction['_id'], approver_name=approver_name, _external=True)
    
#     body = f"""
#     <html>
#     <body>
#         <p>You have a pending approval request for {transaction['employee_name']} from {transaction['department']} department.</p>
#         <p>Use the buttons below to take action:</p>
#         <p>
#             <a href="{approve_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: green; color: white; text-decoration: none;">Approve</a>
#             <a href="{reject_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: red; color: white; text-decoration: none;">Reject</a>
#             <a href="{changes_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: orange; color: white; text-decoration: none;">Request Changes</a>
#         </p>
#     </body>
#     </html>
#     """
    
#     msg = MIMEMultipart()
#     msg['From'] = from_email
#     msg['To'] = to_email
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'html'))

#     try:
#         with smtplib.SMTP('smtp.gmail.com', 587) as server:
#             server.starttls()
#             server.login(from_email, password)
#             server.send_message(msg)
#     except smtplib.SMTPAuthenticationError as auth_err:
#         current_app.logger.error(f"SMTP Authentication Error: {auth_err}")
#         raise
#     except Exception as e:
#         current_app.logger.error(f"Failed to send email: {e}")
#         raise

# @transaction_bp.route('/update_status/<transaction_id>/<status>', methods=['GET'])
# def update_approval_status(transaction_id, status):
#     transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})
#     if not transaction:
#         return jsonify({"error": "Transaction not found"}), 404

#     approver_name = request.args.get("approver_name")
#     for approval in transaction['approvals']:
#         if approval['manager_name'] == approver_name:
#             approval['local_status'] = status
#             break

#     if status == 'approved':
#         next_level = approval['manager_level'] + 1
#         next_approver = current_app.mongo.db.managers.find_one({"department": transaction['department'], "level": next_level})
#         if next_approver:
#             transaction['approvals'].append({"manager_name": next_approver['manager_name'], "manager_level": next_level, "local_status": "pending", "reminder_sent": False})
#         else:
#             transaction['global_status'] = 'approved'
#     else:
#         transaction['global_status'] = 'rejected'

#     current_app.mongo.db.transactions.update_one(
#         {"_id": ObjectId(transaction_id)},
#         {"$set": {"approvals": transaction['approvals'], "global_status": transaction['global_status']}}
#     )
#     return jsonify({"message": "Approval status updated", "transaction": str(transaction['_id'])}), 200

# @transaction_bp.route('/request_changes_form/<transaction_id>', methods=['GET'])
# def request_changes_form(transaction_id):
#     approver_name = request.args.get("approver_name")
#     return f"""
#     <html>
#     <body>
#         <form action="/api/transactions/{transaction_id}/request_changes" method="post">
#             <input type="hidden" name="approver_name" value="{approver_name}">
#             <textarea name="change_request" placeholder="Enter your change request"></textarea>
#             <button type="submit">Submit</button>
#         </form>
#     </body>
#     </html>
#     """

# @transaction_bp.route('/request_changes/<transaction_id>', methods=['POST'])
# def request_changes(transaction_id):
#     approver_name = request.form.get("approver_name")
#     change_request = request.form.get("change_request")
#     transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})
#     if not transaction:
#         return jsonify({"error": "Transaction not found"}), 404

#     for approval in transaction['approvals']:
#         if approval['manager_name'] == approver_name:
#             approval['local_status'] = 'changes_requested'
#             break

#     transaction['taken_actions'].append({"approved_by": approver_name, "taken_actions": change_request})
#     current_app.mongo.db.transactions.update_one(
#         {"_id": ObjectId(transaction_id)},
#         {"$set": {"approvals": transaction['approvals'], "taken_actions": transaction['taken_actions']}}
#     )
#     return jsonify({"message": "Change request submitted", "transaction": str(transaction['_id'])}), 200



















from flask import Blueprint, request, jsonify, current_app, url_for
from bson.objectid import ObjectId
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

transaction_bp = Blueprint('transaction_bp', __name__)

@transaction_bp.route('/', methods=['POST'])
def create_transaction():
    data = request.get_json()

    # Fetch the employee details from the database using employee_id
    employee = current_app.mongo.db.employees.find_one({"employee_id": data['employee_id']})
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    transaction = {
        'employee_name': employee['employee_name'],
        'employee_id': data['employee_id'],
        'conditions_statements': data['conditions_statements'],
        'department': employee['department'],  # Get department from employee record
        'global_status': 'pending',
        'approvals': [],
        'taken_actions': [],
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }

    managers = current_app.mongo.db.managers.find({"department": employee['department']}).sort("level", 1)
    for manager in managers:
        transaction['approvals'].append({
            "manager_name": manager['manager_name'],
            "manager_level": manager['level'],
            "email": manager['email'],
            "local_status": "pending",
            "reminder_sent": False
        })

    transaction_id = current_app.mongo.db.transactions.insert_one(transaction).inserted_id
    transaction['_id'] = str(transaction_id)

    # Send reminder to the level 1 manager
    if transaction['approvals']:
        first_approver = transaction['approvals'][0]
        send_email_reminder(first_approver['email'], transaction, first_approver['manager_name'])

    return jsonify({"message": "Transaction created", "transaction": transaction}), 201

@transaction_bp.route('/reminders', methods=['POST'])
def send_reminders():
    data = request.get_json()
    employee_id = data.get('employee_id')
    
    if not employee_id:
        return jsonify({"error": "'employee_id' is required."}), 400
    
    transaction = current_app.mongo.db.transactions.find_one({"employee_id": employee_id, "global_status": "pending"})
    
    if not transaction:
        return jsonify({"error": "Transaction not found for the provided employee_id."}), 404
    
    for approval in transaction['approvals']:
        if approval['local_status'] == 'pending' and not approval['reminder_sent']:
            approver = current_app.mongo.db.managers.find_one({"manager_name": approval['manager_name']})
            if approver:
                send_email_reminder(approver['email'], transaction, approval['manager_name'])
                approval['reminder_sent'] = True
                current_app.mongo.db.transactions.update_one(
                    {"_id": ObjectId(transaction['_id'])},
                    {"$set": {"approvals": transaction['approvals']}}
                )
            break
    
    return jsonify({"message": "Reminders sent"}), 200

def send_email_reminder(to_email, transaction, approver_name):
    from_email = current_app.config['MAIL_USERNAME']
    password = current_app.config['MAIL_PASSWORD']

    # Debugging statements to ensure credentials are set
    print(f"Sending email from: {from_email}")
    print(f"Email password is set: {'Yes' if password else 'No'}")

    if not from_email or not password:
        raise ValueError("Email credentials are not set")

    subject = "Approval Reminder"
    approve_url = url_for('transaction_bp.update_approval_status', transaction_id=transaction['_id'], status='approved', approver_name=approver_name, _external=True)
    reject_url = url_for('transaction_bp.update_approval_status', transaction_id=transaction['_id'], status='rejected', approver_name=approver_name, _external=True)
    change_approver_url = url_for('transaction_bp.change_approver_form', transaction_id=transaction['_id'], approver_name=approver_name, _external=True)

    # Format the conditions statements
    conditions_html = "".join([f"<li>{condition}</li>" for condition in transaction['conditions_statements']])

    body = f"""
    <html>
    <body>
        <p>You have a pending approval request for {transaction['employee_name']} from {transaction['department']} department.</p>
        <p>Conditions:</p>
        <ul>
            {conditions_html}
        </ul>
        <p>Use the buttons below to take action:</p>
        <p>
            <a href="{approve_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: green; color: white; text-decoration: none;">Approve</a>
            <a href="{reject_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: red; color: white; text-decoration: none;">Reject</a>
            <a href="{change_approver_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: blue; color: white; text-decoration: none;">Change Approver</a>
        </p>
    </body>
    </html>
    """
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
    except smtplib.SMTPAuthenticationError as auth_err:
        current_app.logger.error(f"SMTP Authentication Error: {auth_err}")
        raise
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {e}")
        raise

@transaction_bp.route('/update_status/<transaction_id>/<status>', methods=['GET'])
def update_approval_status(transaction_id, status):
    transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404

    approver_name = request.args.get("approver_name")
    if not approver_name:
        return jsonify({"error": "'approver_name' is required"}), 400

    for approval in transaction['approvals']:
        if approval['manager_name'] == approver_name:
            approval['local_status'] = status
            break

    # Append the action taken by the manager to the taken_actions array
    transaction['taken_actions'].append({
        "manager_name": approver_name,
        "action": status,
        "timestamp": datetime.utcnow()
    })

    if status == 'approved':
        next_level = approval['manager_level'] + 1
        # Check if next level manager is already in the approvals array
        if not any(approval['manager_level'] == next_level for approval in transaction['approvals']):
            next_approver = current_app.mongo.db.managers.find_one({"department": transaction['department'], "level": next_level})
            if next_approver:
                transaction['approvals'].append({"manager_name": next_approver['manager_name'], "manager_level": next_level, "local_status": "pending", "reminder_sent": False})
            else:
                transaction['global_status'] = 'approved'
    else:
        transaction['global_status'] = 'rejected'

    current_app.mongo.db.transactions.update_one(
        {"_id": ObjectId(transaction_id)},
        {"$set": {"approvals": transaction['approvals'], "global_status": transaction['global_status'], "taken_actions": transaction['taken_actions']}}
    )
    return jsonify({"message": "Approval status updated", "transaction": str(transaction['_id'])}), 200

@transaction_bp.route('/change_approver_form/<transaction_id>', methods=['GET'])
def change_approver_form(transaction_id):
    approver_name = request.args.get("approver_name")
    if not approver_name:
        return jsonify({"error": "'approver_name' is required"}), 400

    managers = current_app.mongo.db.managers.find()

    options_html = "".join([f'<option value="{manager["manager_id"]}">{manager["manager_name"]}</option>' for manager in managers])

    return f"""
    <html>
    <body>
        <form action="/api/transactions/{transaction_id}/change_approver" method="post">
            <input type="hidden" name="current_approver_name" value="{approver_name}">
            <label for="new_approver_id">Select new approver:</label>
            <select name="new_approver_id" id="new_approver_id">
                {options_html}
            </select>
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    """

@transaction_bp.route('/change_approver/<transaction_id>', methods=['POST'])
def change_approver(transaction_id):
    current_approver_name = request.form.get("current_approver_name")
    new_approver_id = request.form.get("new_approver_id")

    if not current_approver_name or not new_approver_id:
        return jsonify({"error": "'current_approver_name' and 'new_approver_id' are required"}), 400

    transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404

    new_approver = current_app.mongo.db.managers.find_one({"manager_id": new_approver_id})
    if not new_approver:
        return jsonify({"error": "New approver not found"}), 404

    # Update the approval list
    for approval in transaction['approvals']:
        if approval['manager_name'] == current_approver_name:
            approval['manager_name'] = new_approver['manager_name']
            approval['manager_level'] = new_approver['level']
            approval['email'] = new_approver['email']
            approval['local_status'] = 'pending'
            approval['reminder_sent'] = False
            break

    current_app.mongo.db.transactions.update_one(
        {"_id": ObjectId(transaction_id)},
        {"$set": {"approvals": transaction['approvals']}}
    )

    # Send reminder to the new approver
    send_email_reminder(new_approver['email'], transaction, new_approver['manager_name'])

    return jsonify({"message": "Approver changed and reminder sent", "transaction": str(transaction['_id'])}), 200
