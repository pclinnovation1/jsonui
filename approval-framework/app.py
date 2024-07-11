# app.py
from flask import Flask
from flask_pymongo import PyMongo
from controllers.process_controller import process_bp
from controllers.approver_controller import approver_bp
#from controllers.condition_controller import condition_bp
from controllers.approval_rule_controller import approval_rule_bp
from controllers.transaction_controller import transaction_bp
from routes.api import api_bp

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize PyMongo
mongo = PyMongo(app)

# Make `mongo` available globally
app.mongo = mongo

# Register blueprints
app.register_blueprint(process_bp, url_prefix='/api/processes')
app.register_blueprint(approver_bp, url_prefix='/api/approvers')
#app.register_blueprint(condition_bp, url_prefix='/api')
app.register_blueprint(approval_rule_bp, url_prefix='/api')
app.register_blueprint(transaction_bp, url_prefix='/api')
app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)



