from flask import Flask
from pymongo import MongoClient
from bson import ObjectId
from wrapper_Leave_Acc import update_or_insert_leave_accrual
import datetime

app = Flask(__name__)

# MongoDB client setup
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')  # Adjust the connection string as necessary
db = client['PCL_Interns']  # Database name

def process_learning_alerts():
    status = "process_learning_alerts"
    return status

def sync_instructor_led_training_for_learning():
    status = "sync_instructor_led_training_for_learning"
    return status

def process_learning_records():
    status = "process_learning_records"
    return status

def process_learning_recommendations():
    status = "process_learning_recommendations"
    return status
def mass_assign_goals():
    status = "mass_assign_goals"
    return status

def approval():
    status = "approval"
    return status
    
def course_recommendation():
    status = "course_recommendation"
    return status

       

if __name__ == "__main__":
    # Example population filters for debugging
    

    # Start the Flask app
    app.run(debug=True)
