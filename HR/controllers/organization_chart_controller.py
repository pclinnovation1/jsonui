

from flask import request, jsonify, Blueprint
from pymongo import MongoClient
import config

# Establish connection to MongoDB
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
collection = db[config.EMPLOYEE_DETAIL_COLLECTION_NAME]

organizational_chart_blueprint = Blueprint('organizational_chart', __name__)

def append_to_hierarchy(hierarchy, person, current_level):
    hierarchy.append({
        "level": current_level,
        "person_name": person.get("person_name"),
        "job_title": person.get("job_title"),
        "department": person.get("department"),
        "organization_unit": person.get("organization_unit"),
        "manager_name": person.get("manager_name")
    })

@organizational_chart_blueprint.route('/view', methods=['POST'])
def access_organizational_chart():
    try:
        # Extract data from the request
        data = request.get_json()
        person_name = data.get('person_name')
        levels_above = data.get('levels_above')
        levels_below = data.get('levels_below')

        # Validate the input data
        if not person_name:
            return jsonify({"error": "person_name is required"}), 400

        # Fetch employee details from MongoDB
        employee = collection.find_one({"person_name": person_name})
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        # Helper function to fetch hierarchy above
        def get_hierarchy_above(person_name, levels=None, current_level=1):
            hierarchy = []
            current_person = collection.find_one({"person_name": person_name})
            while current_person and (levels is None or current_level <= levels):
                manager_name = current_person.get("manager_name")
                if manager_name:
                    manager = collection.find_one({"person_name": manager_name})
                    if manager:
                        append_to_hierarchy(hierarchy, manager, current_level)
                        current_person = manager
                        current_level += 1
                    else:
                        break
                else:
                    break
            return hierarchy

        # Helper function to fetch hierarchy below
        def get_hierarchy_below(person_name, levels=None, current_level=1):
            hierarchy = []
            direct_reports = list(collection.find({"manager_name": person_name}))
            for report in direct_reports:
                append_to_hierarchy(hierarchy, report, current_level)
                if levels is None or current_level < levels:
                    hierarchy.extend(get_hierarchy_below(report.get("person_name"), levels, current_level + 1))
            return hierarchy

        # Fetch hierarchy above the employee
        hierarchy_above = get_hierarchy_above(person_name, levels_above)

        # Fetch hierarchy below the employee
        hierarchy_below = get_hierarchy_below(person_name, levels_below)

        # Construct the response
        response = {
            "employee_details": {
                "person_name": employee.get("person_name"),
                "person_number": employee.get("person_number"),
                "job_title": employee.get("job_title"),
                "department": employee.get("department"),
                "manager_name": employee.get("manager_name"),
                "organization_unit": employee.get("organization_unit"),
                "location": employee.get("location")
            },
            "levels_above": hierarchy_above,
            "levels_below": hierarchy_below
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500





# 5.
# i) view
# http://127.0.0.1:5000/organizational_chart/view

# for manual levels 

# {
#   "person_name": "Mauri Salovaara",
#   "levels_above": 8,
#   "levels_below": 3
# }

# or by default all level for above and below

# {
#   "person_name": "Mauri Salovaara"
# }