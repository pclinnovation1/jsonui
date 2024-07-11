from pymongo import MongoClient
import gridfs
from bson import ObjectId

# Database setup
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
db = client['PCL_Interns']
fs = gridfs.GridFS(db)

def read_file_from_gridfs(file_id):
    try:
        # Fetch the file using GridFS
        file = fs.get(file_id)
        # Read the file content
        content = file.read()
        return content
    except gridfs.errors.NoFile:
        return f"No file found with id: {file_id}"

# Example file IDs (replace with your actual IDs)
log_file_id = '668ea3ce3a743d31dd49bbb6'
report_file_id = '668ea3cf3a743d31dd49bbba'

# Read the log file content
log_content = read_file_from_gridfs(ObjectId(log_file_id))
if isinstance(log_content, bytes):
    with open('log.txt', 'wb') as f:
        f.write(log_content)
    print("Log file saved as log.txt")
else:
    print(log_content)

# Read the report file content
report_content = read_file_from_gridfs(ObjectId(report_file_id))
if isinstance(report_content, bytes):
    with open('report.pdf', 'wb') as f:
        f.write(report_content)
    print("Report file saved as report.pdf")
else:
    print(report_content)
