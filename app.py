from flask import Flask, jsonify
import os
from dotenv import load_dotenv
from algorithms.general_algo import connect_database

load_dotenv()

# from routes.LRN.course import course_bp
from routes.max_routes import max_routes_bp
from routes.ABS.leave import leave_bp
from routes.HRM.process_hr_info import hrm_bp
from routes.APR.approval_management import approval_management_bp
from routes.APR.transaction_controller import transaction_controller_bp
from algorithms.SCH.email_sending import email_bp
from routes.LRN.community import community_bp
from routes.JRN.journey import journey_bp

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Custom error handler for rate limiting
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="ratelimit exceeded"), 429


app.register_blueprint(max_routes_bp, url_prefix='/')
# app.register_blueprint(course_bp, url_prefix='/course')
app.register_blueprint(leave_bp, url_prefix='/leave')
app.register_blueprint(hrm_bp, url_prefix='/')
app.register_blueprint(approval_management_bp, url_prefix='/')
app.register_blueprint(transaction_controller_bp, url_prefix='/')
app.register_blueprint(email_bp, url_prefix='/')
app.register_blueprint(community_bp, url_prefix='/community')
app.register_blueprint(journey_bp, url_prefix='/journey')



if __name__ == '__main__':
    connect_database()
    print("server started")
    app.run(debug=True, host="0.0.0.0", port=5001)
