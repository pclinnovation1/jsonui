
#####
from flask import Blueprint
from controllers.process_controller import process_bp
from controllers.approval_rule_controller import approval_rule_bp
from controllers.approver_controller import approver_bp
# from controllers.condition_controller import condition_bp
from controllers.email_reminder_controller import email_reminder_bp
from controllers.transaction_controller import transaction_bp

api_bp = Blueprint('api', __name__)

api_bp.register_blueprint(process_bp, url_prefix='/processes')
api_bp.register_blueprint(approval_rule_bp, url_prefix='/approval_rules')
api_bp.register_blueprint(approver_bp, url_prefix='/approvers')
# api_bp.register_blueprint(condition_bp, url_prefix='/conditions')
api_bp.register_blueprint(email_reminder_bp, url_prefix='/email_reminders')
api_bp.register_blueprint(transaction_bp, url_prefix='/transactions')
