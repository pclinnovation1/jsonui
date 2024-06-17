# config.py
from flask import Flask
from flask_mail import Mail
from pymongo import MongoClient

app = Flask(__name__)

# Configure MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['PCL_Interns']

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ankitpcl766@gmail.com' # ur mail id
app.config['MAIL_PASSWORD'] = 'gzwh llii xvoz fhzc' # password

mail = Mail(app)
