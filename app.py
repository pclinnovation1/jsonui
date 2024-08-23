from flask import Flask


from controllers.performance_document_type_controller_01 import performance_document_type_bp
from controllers.questionnaire_controller_02 import questionnaire_bp
from controllers.feedback_template_controller_03 import feedback_template_bp
from controllers.check_in_template_controller_04 import check_in_template_bp
from controllers.competency_controller_05 import competency_bp
from controllers.overall_performance_controller_06 import overall_performance_bp
from controllers.participant_feedback_controller_07 import participant_feedback_template_bp
from controllers.performance_template_controller_08 import performance_template_bp
from controllers.performance_template_connection_controller_09 import performance_template_connection_bp
from controllers.my_performance_controller_10 import my_performance_bp
from controllers.eligible_employee_controller_11 import eligible_employee_bp

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
# 6
app.register_blueprint(overall_performance_bp, url_prefix='/overall_performance')
# 7
app.register_blueprint(participant_feedback_template_bp, url_prefix='/participant_feedback')
# 8collection name - PERFORMANCE_TEMPLATE_COLLECTION_NAME = "P_PerformanceTemplates"
# doubtful..? which route will come first, below one or this one - 3+4+5+6+7
app.register_blueprint(performance_template_bp, url_prefix='/performance_templates')
# 9collection name - PERFORMANCE_TEMPLATE_CONNECTION_COLLECTION_NAME = "P_Performance_template_connection"
app.register_blueprint(performance_template_connection_bp, url_prefix='/performance_template_connections')
# 10collection name - MY_PERFORMANCE_COLLECTION_NAME = "P_Performance_document"
app.register_blueprint(my_performance_bp, url_prefix='/my_performances')
# 11
app.register_blueprint(eligible_employee_bp, url_prefix='/eligible_employee')




if __name__ == '__main__':  
    app.run(debug=True)
