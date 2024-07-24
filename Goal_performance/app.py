
from flask import Flask
from controllers.goals_controller import goals_bp
from controllers.eligibility_profile_controller import eligibility_profile_bp
from controllers.review_period_controller import review_period_bp
from controllers.goal_plan_controller import goal_plan_bp
from controllers.my_goals_controller import my_goals_bp  # Import the new controller

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(goals_bp, url_prefix='/goals')
app.register_blueprint(eligibility_profile_bp, url_prefix='/eligibility_profiles')
app.register_blueprint(review_period_bp, url_prefix='/review_periods')
app.register_blueprint(goal_plan_bp, url_prefix='/goal_plans')
app.register_blueprint(my_goals_bp, url_prefix='/my_goals')  # Register the new blueprint

if __name__ == '__main__':  
    app.run(debug=True)




