

from flask import Flask

from controllers.eligibility_profile_controller import eligibility_profile_bp
from controllers.eligibility_batch_process_controller import eligibility_batch_process_bp
from controllers.review_period_controller import review_period_bp
from controllers.performance_role_controller import performance_role_bp
from controllers.performance_process_flow_controller import process_flow_bp
from controllers.performance_document_type_controller import performance_document_type_bp
from controllers.feedback_template_controller import feedback_template_bp
from controllers.check_in_template_controller import check_in_template_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(eligibility_profile_bp, url_prefix='/eligibility_profiles')
app.register_blueprint(eligibility_batch_process_bp, url_prefix='/eligibility_batch_process')
app.register_blueprint(review_period_bp, url_prefix='/review_periods')
app.register_blueprint(performance_role_bp, url_prefix='/performance_roles')
app.register_blueprint(process_flow_bp, url_prefix='/performance_process_flows')
app.register_blueprint(performance_document_type_bp, url_prefix='/performance_document_types')
app.register_blueprint(feedback_template_bp, url_prefix='/feedback_templates')
app.register_blueprint(check_in_template_bp, url_prefix='/check_in_templates')


if __name__ == '__main__':  
    app.run(debug=True)






