from flask import Flask

from controllers.eligibility_profile_controller import eligibility_profile_bp
from controllers.eligibility_batch_process_controller import eligibility_batch_process_bp
from controllers.review_period_controller import review_period_bp
from controllers.performance_role_controller import performance_role_bp
from controllers.performance_process_flow_controller import process_flow_bp
from controllers.performance_template_controller import performance_template_bp
from controllers.performance_document_type_controller import performance_document_type_bp
from controllers.questionnaire_controller import questionnaire_bp
from controllers.feedback_template_controller import feedback_template_bp
from controllers.check_in_template_controller import check_in_template_bp
from controllers.my_performance_controller import my_performance_bp
from controllers.performance_template_connection_controller import performance_template_connection_bp
from controllers.competency_controller import competency_bp
from controllers.participant_feedback_controller import participant_feedback_template_bp
from controllers.overall_performance_controller import overall_performance_bp
from controllers.eligible_employee_controller import eligible_employee_bp
from controllers.assign_performance_controller import assign_performance_bp  # Import the new blueprint
from controllers.assign_peer_controller import assign_peer_bp
from controllers.send_email_360 import peer_feedback_bp
from controllers.notify_performance_controller import notify_performance_bp
# Register the blueprint

app = Flask(__name__)

# 1collection name - PERFORMANCE_DOCUMENT_TYPE_COLLECTION_NAME = "P_PerformanceDocumentTypes"
app.register_blueprint(performance_document_type_bp, url_prefix='/performance_document_types')

# 2collection name - QUESTIONNAIRE_COLLECTION_NAME = "P_Questionnaires"
app.register_blueprint(questionnaire_bp, url_prefix='/questionnaires')

# 3collection name - FEEDBACK_TEMPLATE_COLLECTION_NAME = "P_FeedbackTemplates" (add 2)
app.register_blueprint(feedback_template_bp, url_prefix='/feedback_templates')

# 4collection name - CHECK_IN_TEMPLATE_COLLECTION_NAME = "P_CheckInTemplates"
app.register_blueprint(check_in_template_bp, url_prefix='/check_in_templates')

#5 competency
app.register_blueprint(competency_bp, url_prefix='/add_competency')

# 6collection name - PERFORMANCE_TEMPLATE_COLLECTION_NAME = "P_PerformanceTemplates"
# doubtful..? which route will come first, below one or this one - 3+4+5
app.register_blueprint(performance_template_bp, url_prefix='/performance_templates')

# 7ollection name - PERFORMANCE_TEMPLATE_CONNECTION_COLLECTION_NAME = "P_Performance_template_connection"
app.register_blueprint(performance_template_connection_bp, url_prefix='/performance_template_connections')

# add 360 degree review

# 8collection name - MY_PERFORMANCE_COLLECTION_NAME = "P_Performance_document"
app.register_blueprint(my_performance_bp, url_prefix='/my_performances')

# collection name - ELIGIBILITY_BATCH_PROCESS_COLLECTION_NAME = "P_EligibilityBatchProcess"
app.register_blueprint(eligibility_batch_process_bp, url_prefix='/eligibility_batch_process')

# Register Blueprints
# collection name - PERFORMANCE_ROLE_COLLECTION_NAME = "P_PerformanceRoles"
app.register_blueprint(performance_role_bp, url_prefix='/performance_roles')

# collection name - PERFORMANCE_PROCESS_FLOW_COLLECTION_NAME = "P_PerformanceProcessFlows" not using
app.register_blueprint(process_flow_bp, url_prefix='/performance_process_flows')

app.register_blueprint(participant_feedback_template_bp, url_prefix='/participant_feedback')

app.register_blueprint(overall_performance_bp, url_prefix='/overall_performance')

# Register the blueprint
app.register_blueprint(eligible_employee_bp, url_prefix='/eligible_employee')

app.register_blueprint(assign_performance_bp, url_prefix='/assign_performance')

app.register_blueprint(assign_peer_bp, url_prefix='/peer')

app.register_blueprint(peer_feedback_bp, url_prefix='/peer_feedback')

app.register_blueprint(notify_performance_bp, url_prefix='/notify')

if __name__ == '__main__':  
    app.run(debug=True)






# eligiblity profile nhi lagayi h performance document mein
# comment, submit, feedback, ye sab ke ;iye employee ke liye notification jaaye
