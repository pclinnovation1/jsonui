from flask import Flask
from controllers.goals_controller import goals_bp
from controllers.eligibility_profile_controller import eligibility_profile_bp
from controllers.review_period_controller import review_period_bp
from controllers.include_exclude_controller import include_exclude_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(goals_bp, url_prefix='/goals')
app.register_blueprint(eligibility_profile_bp, url_prefix='/eligibility_profiles')
app.register_blueprint(review_period_bp, url_prefix='/review_periods')
app.register_blueprint(include_exclude_bp, url_prefix='/include_exclude')

if __name__ == '__main__':
    app.run(debug=True)
