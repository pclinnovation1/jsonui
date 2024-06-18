import time
from bson import ObjectId  # Import ObjectId from bson

def generate_letters(param1, param2, process_details_id, db):
    process_details_collection = db['Process_Details']
    
    # Update status to Running
    process_details_collection.update_one(
        {'_id': process_details_id},  # Use process_details_id directly
        {'$set': {'Status': 'Running'}}
    )
    
    # Simulate task execution
    print(f"Generating letters with {param1} and {param2}...")
    time.sleep(2)
    
    # Update status to Completed
    process_details_collection.update_one(
        {'_id': process_details_id},  # Use process_details_id directly
        {
            '$set': {
                'Status': 'Completed',
                'Completion Time': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
        }
    )
    print("Letters generated.")
