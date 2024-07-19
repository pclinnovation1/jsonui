from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://dev1_user:dev1_pass@172.191.245.199:27017/dev1')
db = client['dev1']

@app.route('/enroll', methods=['POST'])
def enroll_employee():
    data = request.get_json()
    offering_title = data.get("Offering Title")
    enrollment_date = data.get("Enrollment Date")
    offering_number = data.get("Offering Number")
    person_name = data.get("Person Name")
    

    if not offering_title or not person_name or not enrollment_date:
        return jsonify({"error": "Invalid input data"}), 400

    # Find offerings by title
    offerings = list(db['course_offerings'].find({"Offering Title": offering_title}))
    print('offerings1',offerings)
    
    if len(offerings) > 1 and not offering_number:
        multiple_offerings = []
        for offering in offerings:
            multiple_offerings.append({
                "Offering Number": offering["Offering Number"],
                "Offering Title": offering["Offering Title"],
                "Offering Format": offering["Offered Format"],
                "Active Learners": offering["Active Learners"],
                "Maximum Learners": offering["Maximum Capacity"]
            })
        return jsonify({
            "error": "There are multiple offerings with this title. Please specify the Offering Number.",
            "offerings": multiple_offerings
        }), 400

    if not offerings:
        return jsonify({"error": "Offering not found."}), 404

    print('offering_number1',offering_number)
    # Use the Offering Number if provided
    if offering_number:
        offering = db['course_offerings'].find_one({"Offering Number": offering_number})
    else:
        offering = offerings[0]

     # Check if offering was found
    if offering is None:
        return jsonify({"error": f"No course offering found with Offering Number '{offering_number}'."}), 400
    
    print('Offering2',offering)
    print('Offered_format1',offering["Offered Format"])
    # Check if the course is Instructor-Led
    if offering["Offered Format"] != "Instructor-Led":
        return jsonify({"error": f"The course offering with title '{offering_title}' is not Instructor-Led."}), 400
    
    # Split Person Name into First Name and Last Name
    try:
        first_name, last_name = person_name.split(" ", 1)
    except ValueError:
        return jsonify({"error": "Invalid Person Name format"}), 400

    # Find Person Number from EmployeeDetails_UK
    employee = db['EmployeeDetails_UK'].find_one({"First_Name": first_name, "Last_Name": last_name})
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    person_number = employee["Person_Number"]
    
      # Check if the employee is already enrolled or has withdrawn from the course offering
    existing_enrollment = db['employee_offering_details'].find_one({
        "Person Number": person_number,
        "Offering Number": offering["Offering Number"],
        "Current Status": {"$in": ["in-progress", "completed", "withdrawn"]}
    })
    
    if existing_enrollment:
        current_status = existing_enrollment["Current Status"]
        return jsonify({"error": f"Employee is already enrolled in this course offering with status '{current_status}'."}), 400


    # Count the number of active learners for this offering number
    active_learners_count = db['employee_offering_details'].count_documents(
        {"Offering Number": offering["Offering Number"], "Current Status": "in-progress"}
    )

    # Split Person Name into First Name and Last Name
    try:
        first_name, last_name = person_name.split(" ", 1)
    except ValueError:
        return jsonify({"error": "Invalid Person Name format"}), 400

    # Find Person Number from EmployeeDetails_UK
    employee = db['EmployeeDetails_UK'].find_one({"First_Name": first_name, "Last_Name": last_name})
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    person_number = employee["Person_Number"]

    employee_details = {
        "Person Number": person_number,
        "Employee Name": person_name,
        "Enrollment Date": enrollment_date,
        "Enrolled Status": "in-progress",
        "Current Status": "in-progress"
    }

    if active_learners_count < offering["Maximum Capacity"]:
        # Enroll the employee
        db['employee_offering_details'].insert_one({
            "offering_id": offering["_id"],
            "Offering Number": offering["Offering Number"],
            "Offering Title": offering_title,
            **employee_details
        })
        return jsonify({"message": "Employee enrolled successfully."}), 200
    else:
        # Calculate next waitlist number
        waitlist_count = db['employee_offering_details'].count_documents(
            {"Offering Number": offering["Offering Number"], "Current Status": "waitlist"}
        )
        waitlist_number = waitlist_count + 1

        # Add to waitlist
        employee_details_wl = {
            "Person Number": person_number,
            "Employee Name": person_name,
            "Enrollment Date": enrollment_date,
            "Enrolled Status": f"waitlist {waitlist_number}",
            "Current Status": "waitlist",
            "Waitlist Number": waitlist_number
        }
        db['employee_offering_details'].insert_one({
            "offering_id": offering["_id"],
            "Offering Number": offering["Offering Number"],
            "Offering Title": offering_title,
            **employee_details_wl
        })
        return jsonify({"message": f"Seats are full. Employee added to waitlist with waitlist number {waitlist_number}."}), 200

@app.route('/withdraw', methods=['POST'])
def withdraw_employee():
    data = request.get_json()
    offering_title = data.get("Offering Title")
    offering_number = data.get("Offering Number")
    person_name = data.get("Person Name")

    if not offering_title or not person_name:
        return jsonify({"error": "Invalid input data"}), 400

    # Find offerings by title
    offerings = list(db['course_offerings'].find({"Offering Title": offering_title}))
    
    if len(offerings) > 1 and not offering_number:
        multiple_offerings = []
        for offering in offerings:
            multiple_offerings.append({
                "Offering Number": offering["Offering Number"],
                "Offering Format": offering["Offered Format"],
                "Active Learners": offering["Active Learners"],
                "Maximum Learners": offering["Maximum Capacity"]
            })
        return jsonify({
            "error": "There are multiple offerings with this title. Please specify the Offering Number.",
            "offerings": multiple_offerings
        }), 400

    if not offerings:
        return jsonify({"error": "Offering not found."}), 404

    # Use the Offering Number if provided
    if offering_number:
        offering = db['course_offerings'].find_one({"Offering Number": offering_number})
    else:
        offering = offerings[0]

    # Check if the course is Instructor-Led
    if offering["Offered Format"] != "Instructor-Led":
        return jsonify({"error": f"The course offering with title '{offering_title}' is not Instructor-Led."}), 400

    # Split Person Name into First Name and Last Name
    try:
        first_name, last_name = person_name.split(" ", 1)
    except ValueError:
        return jsonify({"error": "Invalid Person Name format"}), 400

    # Find Person Number from EmployeeDetails_UK
    employee = db['EmployeeDetails_UK'].find_one({"First_Name": first_name, "Last_Name": last_name})
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    person_number = employee["Person_Number"]

    offering_id = offering["_id"]
    enrolled_employee = db['employee_offering_details'].find_one(
        {"offering_id": offering_id, "Person Number": person_number}
    )
    if enrolled_employee:
        if enrolled_employee["Current Status"] == "withdrawn":
            return jsonify({"error": "Employee has already withdrawn from the course."}), 400

        result = db['employee_offering_details'].update_one(
            {"offering_id": offering_id, "Person Number": person_number, "Current Status": "in-progress"},
            {"$set": {"Current Status": "withdrawn"}}
        )
        if result.matched_count > 0:
            # Check for waitlisted employees
            waitlisted_employee = db['employee_offering_details'].find_one(
                {"offering_id": offering_id, "Current Status": "waitlist"},
                sort=[("Waitlist Number", 1)]
            )

            if waitlisted_employee:
                # Remove from waitlist and add to enrolled
                db['employee_offering_details'].update_one(
                    {"_id": waitlisted_employee["_id"]},
                    {"$set": {"Current Status": "in-progress"}, "$unset": {"Waitlist Number": ""}}
                )

                # Decrease waitlist numbers for remaining waitlisted employees
                db['employee_offering_details'].update_many(
                    {"offering_id": offering_id, "Waitlist Number": {"$gt": waitlisted_employee["Waitlist Number"]}},
                    {"$inc": {"Waitlist Number": -1}}
                )

            return jsonify({"message": "Employee withdrawn successfully and waitlist updated."}), 200
        else:
            return jsonify({"error": "Employee not enrolled in the specified offering."}), 404
    else:
        return jsonify({"error": "Employee not enrolled in the specified offering."}), 404

if __name__ == '__main__':
    app.run(debug=True)
