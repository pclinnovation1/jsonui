from flask import Blueprint, request, jsonify, current_app, url_for, render_template, render_template_string
from bson.objectid import ObjectId
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

transaction_bp = Blueprint('transaction_bp', __name__, url_prefix='/api/transactions')

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
        first_manager = transaction['approvals'][0]
        send_email_reminder(first_manager['email'], transaction, first_manager['manager_name'])

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
            manager = current_app.mongo.db.managers.find_one({"manager_name": approval['manager_name']})
            if manager:
                send_email_reminder(manager['email'], transaction, approval['manager_name'])
                approval['reminder_sent'] = True
                current_app.mongo.db.transactions.update_one(
                    {"_id": ObjectId(transaction['_id'])},
                    {"$set": {"approvals": transaction['approvals']}}
                )
            break
    
    return jsonify({"message": "Reminders sent"}), 200

def send_email_reminder(to_email, transaction, manager_name):
    from_email = current_app.config['MAIL_USERNAME']
    password = current_app.config['MAIL_PASSWORD']

    # Debugging statements to ensure credentials are set
    print(f"Sending email from: {from_email}")
    print(f"Email password is set: {'Yes' if password else 'No'}")

    if not from_email or not password:
        raise ValueError("Email credentials are not set")

    subject = "Approval Reminder"
    approve_url = url_for('transaction_bp.update_approval_status', transaction_id=transaction['_id'], status='approved', manager_name=manager_name, _external=True)
    reject_url = url_for('transaction_bp.update_approval_status', transaction_id=transaction['_id'], status='rejected', manager_name=manager_name, _external=True)
    add_manager_url = url_for('transaction_bp.add_manager_form', transaction_id=transaction['_id'], manager_name=manager_name, _external=True)
    request_change_url = url_for('transaction_bp.request_changes_form', transaction_id=transaction['_id'], manager_name=manager_name, _external=True)

    # Render the email template
    body = render_template('email_reminder.html', transaction=transaction, approve_url=approve_url, reject_url=reject_url, request_change_url=request_change_url, add_manager_url=add_manager_url)
    
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

    manager_name = request.args.get("manager_name")
    if not manager_name:
        return jsonify({"error": "'manager_name' is required"}), 400

    for approval in transaction['approvals']:
        if approval['manager_name'] == manager_name:
            approval['local_status'] = status
            break

    # Append the action taken by the manager to the taken_actions array
    transaction['taken_actions'].append({
        "manager_name": manager_name,
        "action": status,
        "timestamp": datetime.utcnow()
    })

    if status == 'approved':
        next_level = approval['manager_level'] + 1
        # Check if next level manager is already in the approvals array
        if not any(approval['manager_level'] == next_level for approval in transaction['approvals']):
            next_manager = current_app.mongo.db.managers.find_one({"department": transaction['department'], "level": next_level})
            if next_manager:
                transaction['approvals'].append({"manager_name": next_manager['manager_name'], "manager_level": next_level, "local_status": "pending", "reminder_sent": False})
            else:
                transaction['global_status'] = 'approved'
    else:
        transaction['global_status'] = 'rejected'

    current_app.mongo.db.transactions.update_one(
        {"_id": ObjectId(transaction_id)},
        {"$set": {"approvals": transaction['approvals'], "global_status": transaction['global_status'], "taken_actions": transaction['taken_actions']}}
    )
    return jsonify({"message": "Approval status updated", "transaction": str(transaction['_id'])}), 200

@transaction_bp.route('/request_changes_form/<transaction_id>', methods=['GET'])
def request_changes_form(transaction_id):
    manager_name = request.args.get("manager_name")
    if not manager_name:
        return jsonify({"error": "'manager_name' is required"}), 400

    return render_template('request_changes_form.html', transaction_id=transaction_id, manager_name=manager_name)

@transaction_bp.route('/request_changes/<transaction_id>', methods=['POST'])
def request_changes(transaction_id):
    manager_name = request.form.get("manager_name")
    change_request = request.form.get("change_request")
    if not manager_name or not change_request:
        return jsonify({"error": "'manager_name' and 'change_request' are required"}), 400

    transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404

    # Append the change request to the taken_actions array
    transaction['taken_actions'].append({
        "manager_name": manager_name,
        "action": "request_change",
        "change_request": change_request,
        "timestamp": datetime.utcnow()
    })

    current_app.mongo.db.transactions.update_one(
        {"_id": ObjectId(transaction_id)},
        {"$set": {"taken_actions": transaction['taken_actions']}}
    )
    return jsonify({"message": "Change request submitted", "transaction": str(transaction['_id'])}), 200

@transaction_bp.route('/add_manager_form/<transaction_id>', methods=['GET'])
def add_manager_form(transaction_id):
    manager_name = request.args.get("manager_name")
    if not manager_name:
        return jsonify({"error": "'manager_name' is required"}), 400

    managers = current_app.mongo.db.managers.find()

    return render_template('add_manager_form.html', transaction_id=transaction_id, manager_name=manager_name, managers=managers)

@transaction_bp.route('/add_manager/<transaction_id>', methods=['POST'])
def add_manager(transaction_id):
    current_manager_name = request.form.get("current_manager_name")
    new_manager_id = request.form.get("new_manager_id")

    if not current_manager_name or not new_manager_id:
        return jsonify({"error": "'current_manager_name' and 'new_manager_id' are required"}), 400

    transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404

    new_manager = current_app.mongo.db.managers.find_one({"manager_id": new_manager_id})
    if not new_manager:
        return jsonify({"error": "New manager not found"}), 404

    # Add the new manager to the approval list
    transaction['approvals'].append({
        "manager_name": new_manager['manager_name'],
        "manager_level": new_manager['level'],
        "email": new_manager['email'],
        "local_status": 'pending',
        "reminder_sent": False
    })

    current_app.mongo.db.transactions.update_one(
        {"_id": ObjectId(transaction_id)},
        {"$set": {"approvals": transaction['approvals']}}
    )

    # Send reminder to the new manager
    send_email_reminder(new_manager['email'], transaction, new_manager['manager_name'])

    return jsonify({"message": "Manager added and reminder sent", "transaction": str(transaction['_id'])}), 200
