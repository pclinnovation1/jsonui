from flask import Flask
from goal_plan import goal_plan_bp
from goal import goal_bp
from eligibility_profile import eligibility_profile_bp
from  review_period import review_period_bp
  # Import the new controller

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(goal_plan_bp, url_prefix='/goal_plan')
app.register_blueprint(goal_bp, url_prefix='/goal')
app.register_blueprint(eligibility_profile_bp, url_prefix='/eligibility')
app.register_blueprint(review_period_bp, url_prefix='/review_period')

if __name__ == '__main__':  
    app.run(debug=True)
