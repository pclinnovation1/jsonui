import time

def assign_courses(param1, param2, param3, process_details_id, db):
    process_details_collection = db['Process_Details']
    
    # Update status to Running
    process_details_collection.update_one(
        {'_id': process_details_id},
        {'$set': {'Status': 'Running'}}
    )
    
    # Simulate task execution
    print(f"Assigning courses with {param1}, {param2}, and {param3}...")
    time.sleep(2)
    
    # Update status to Completed
    process_details_collection.update_one(
        {'_id': process_details_id},
        {
            '$set': {
                'Status': 'Completed',
                'Completion Time': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
        }
    )
    print("Courses assigned.")
