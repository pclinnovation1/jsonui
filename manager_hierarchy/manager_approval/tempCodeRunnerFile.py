import sys
import os
from flask import Flask
from flask_pymongo import PyMongo

# Adjust the sys.path to include the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import controllers directly here to avoid circular import issues
from manager_approval.api.transaction_controller import transaction_bp
from manager_approval.api.manager_controller import manager_bp
from manager_approval.api.employee_controller import employee_bp
from manager_approval.api.condition_controller import condition_bp
from manager_approval.api.approver_controller import approval_bp

app = Flask(__name__)
app.config.from_object('manager_approval.config.config.Config')

# Debug: Print the configuration values to ensure they are set correctly
print("MONGO_URI:", app.config['MONGO_URI'])
print("MAIL_USERNAME:", app.config['MAIL_USERNAME'])
print("MAIL_PASSWORD is set:", 'Yes' if app.config['MAIL_PASSWORD'] else 'No')
print("SECRET_KEY is set:", 'Yes' if app.config['SECRET_KEY'] else 'No')

# Initialize PyMongo
mongo = PyMongo(app)

# Make `mongo` available globally
app.mongo = mongo

# Register blueprints
app.register_blueprint(manager_bp, url_prefix='/api/managers')
app.register_blueprint(employee_bp, url_prefix='/api/employees')
app.register_blueprint(approval_bp, url_prefix='/api/approvals')
app.register_blueprint(condition_bp, url_prefix='/api/conditions')
app.register_blueprint(transaction_bp, url_prefix='/api/transactions')

if __name__ == '__main__':
    app.run(debug=True)
