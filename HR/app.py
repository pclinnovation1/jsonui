from flask import Flask
from pymongo import MongoClient
import config

app = Flask(__name__)

# MongoDB connection
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]


# Import and register blueprints
from controllers.report_controller import report_blueprint
from controllers.employment_controller import employment_blueprint
from controllers.person_controller import person_info_blueprint
from controllers.probation_controller import probation_blueprint
from controllers.organization_chart_controller import organizational_chart_blueprint
from controllers.disciplinary_action_controller import disciplinary_blueprint
from controllers.change_manager_controller import change_manager_blueprint


app.register_blueprint(report_blueprint, url_prefix='/report')
app.register_blueprint(employment_blueprint, url_prefix='/employment')
app.register_blueprint(person_info_blueprint, url_prefix='/person_info')
app.register_blueprint(probation_blueprint, url_prefix='/probation')
app.register_blueprint(organizational_chart_blueprint, url_prefix='/organizational_chart')
app.register_blueprint(disciplinary_blueprint, url_prefix='/discipline')
app.register_blueprint(change_manager_blueprint, url_prefix='/change_manager')



if __name__ == '__main__':
    app.run(debug=True)














































