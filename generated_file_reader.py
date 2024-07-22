# from pymongo import MongoClient
# import gridfs
# from bson import ObjectId

# # Database setup
# client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
# db = client['PCL_Interns']
# fs = gridfs.GridFS(db)

# def read_file_from_gridfs(file_id):
#     try:
#         # Fetch the file using GridFS
#         file = fs.get(file_id)
#         # Read the file content
#         content = file.read()
#         return content
#     except gridfs.errors.NoFile:
#         return f"No file found with id: {file_id}"

# # Example file IDs (replace with your actual IDs)
# log_file_id = '669a26cb433b30e12b25affe'
# report_file_id = '669a26cc433b30e12b25b002'

# # Read the log file content
# log_content = read_file_from_gridfs(ObjectId(log_file_id))
# if isinstance(log_content, bytes):
#     with open('log.txt', 'wb') as f:
#         f.write(log_content)
#     print("Log file saved as log.txt")
# else:
#     print(log_content)

# # Read the report file content
# report_content = read_file_from_gridfs(ObjectId(report_file_id))
# if isinstance(report_content, bytes):
#     with open('report.pdf', 'wb') as f:
#         f.write(report_content)
#     print("Report file saved as report.pdf")
# else:
#     print(report_content)




from pymongo import MongoClient
import gridfs
from bson import ObjectId

# Database setup
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
db = client['PCL_Interns']

# GridFS setup for each collection
fs_log = gridfs.GridFS(db, collection='generated_log')
fs_report = gridfs.GridFS(db, collection='generated_report')

def read_file_from_gridfs(fs, file_id):
    try:
        # Fetch the file using GridFS
        file = fs.get(file_id)
        # Read the file content
        content = file.read()
        return content
    except gridfs.errors.NoFile:
        return f"No file found with id: {file_id}"

# Example file IDs (replace with your actual IDs)
log_file_id = '669e15bd7dd6efab0d6cd7f6'
report_file_id = '669a26cc433b30e12b25b002'

# Read the log file content
log_content = read_file_from_gridfs(fs_log, ObjectId(log_file_id))
if isinstance(log_content, bytes):
    with open('log.txt', 'wb') as f:
        f.write(log_content)
    print("Log file saved as log.txt")
else:
    print(log_content)

# Read the report file content
report_content = read_file_from_gridfs(fs_report, ObjectId(report_file_id))
if isinstance(report_content, bytes):
    with open('report.pdf', 'wb') as f:
        f.write(report_content)
    print("Report file saved as report.pdf")
else:
    print(report_content)
