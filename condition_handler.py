# import re
# from pymongo import MongoClient
# from bson.objectid import ObjectId

# def parse_condition(condition_str):
#     if '|' in condition_str or '&' in condition_str:
#         if '|' in condition_str:
#             values = [val.strip() for val in condition_str.split('|')]
#             value_type = "one_of_these"
#         else:
#             values = [val.strip() for val in condition_str.split('&')]
#             value_type = "all_of_these"
            
#         field, operator = re.match(r'(\w+)\s*(==|>|<|between)', values[0]).groups()
#         values = [re.sub(r'(\w+)\s*(==|>|<|between)\s*', '', val) for val in values]
#     else:
#         match = re.match(r'(\w+)\s*(==|>|<|between)\s*(.+)', condition_str)
#         if match:
#             field, operator, value = match.groups()
#             if operator == 'between':
#                 values = value.split()
#                 value_type = "range"
#             else:
#                 values = [value.strip()]
#                 value_type = "single_value"
#         else:
#             raise ValueError(f"Invalid condition format: {condition_str}")
    
#     condition = {
#         'field': field,
#         'operator': operator,
#         'values': values,
#         'value_type': value_type
#     }
    
#     return condition

# def group_conditions(conditions, num_conditions):
#     grouped_conditions = []
#     temp_group = []
    
#     for condition in conditions:
#         temp_group.append(condition)
#         if len(temp_group) == num_conditions:
#             grouped_conditions.append(temp_group)
#             temp_group = []
    
#     if temp_group:
#         grouped_conditions.append(temp_group)
    
#     return grouped_conditions

# def format_for_mongodb(grouped_conditions):
#     formatted_conditions = []
#     for group in grouped_conditions:
#         for condition in group:
#             value = condition['values']
#             if condition['value_type'] == "single_value":
#                 value = condition['values'][0]
#             elif condition['value_type'] in ["one_of_these", "all_of_these"]:
#                 value = condition['values']
#             elif condition['value_type'] == "range":
#                 value = condition['values']
                
#             formatted_condition = {
#                 "_id": ObjectId(),
#                 "conditionId": str(ObjectId()),
#                 "processId": "example_process_id",  # Replace with actual processId if available
#                 "type": condition['value_type'] if condition['value_type'] in ["all_of_these", "one_of_these", "range"] else "threshold",
#                 "field": condition['field'],
#                 "operator": condition['operator'],
#                 "value": value,
#                 "action": "require_approval_from_manager"  # Replace with actual action if available
#             }
#             formatted_conditions.append(formatted_condition)
#     return formatted_conditions

# def insert_into_mongodb(conditions):
#     client = MongoClient('mongodb://localhost:27017/pdk')  # Replace with your MongoDB URI
#     db = client['pdk']  # Replace with your database name
#     collection = db['convishal']  # Replace with your collection name
#     collection.insert_many(conditions)
#     print(f"Inserted {len(conditions)} conditions into MongoDB")

# # Main function
# def main():
#     num_conditions = int(input("Enter the number of conditions: "))
    
#     conditions = []
#     for i in range(num_conditions):
#         condition_str = input(f"Enter condition {i+1}: ").strip()
#         condition = parse_condition(condition_str)
#         conditions.append(condition)
    
#     grouped_conditions = group_conditions(conditions, num_conditions)
#     formatted_conditions = format_for_mongodb(grouped_conditions)
    
#     print("Extracted Conditions:")
#     for condition in conditions:
#         print(condition)
    
#     print("Grouped Conditions for MongoDB Insertion:")
#     for group in grouped_conditions:
#         print(group)
    
#     print("Formatted Conditions for MongoDB:")
#     for condition in formatted_conditions:
#         print(condition)
    
#     # Insert formatted conditions into MongoDB
#     insert_into_mongodb(formatted_conditions)

# if __name__ == "__main__":
#     main()














########
# condition_handler.py
import re
from pymongo import MongoClient
from bson.objectid import ObjectId

def parse_condition(condition_str):
    if '|' in condition_str or '&' in condition_str:
        if '|' in condition_str:
            values = [val.strip() for val in condition_str.split('|')]
            value_type = "one_of_these"
        else:
            values = [val.strip() for val in condition_str.split('&')]
            value_type = "all_of_these"
            
        field, operator = re.match(r'(\w+)\s*(==|>|<|between)', values[0]).groups()
        values = [re.sub(r'(\w+)\s*(==|>|<|between)\s*', '', val) for val in values]
    else:
        match = re.match(r'(\w+)\s*(==|>|<|between)\s*(.+)', condition_str)
        if match:
            field, operator, value = match.groups()
            if operator == 'between':
                values = value.split()
                value_type = "range"
            else:
                values = [value.strip()]
                value_type = "single_value"
        else:
            raise ValueError(f"Invalid condition format: {condition_str}")
    
    condition = {
        'field': field,
        'operator': operator,
        'values': values,
        'value_type': value_type
    }
    
    return condition

def group_conditions(conditions, num_conditions):
    grouped_conditions = []
    temp_group = []
    
    for condition in conditions:
        temp_group.append(condition)
        if len(temp_group) == num_conditions:
            grouped_conditions.append(temp_group)
            temp_group = []
    
    if temp_group:
        grouped_conditions.append(temp_group)
    
    return grouped_conditions

def format_for_mongodb(grouped_conditions):
    formatted_conditions = []
    for group in grouped_conditions:
        for condition in group:
            value = condition['values']
            if condition['value_type'] == "single_value":
                value = condition['values'][0]
            elif condition['value_type'] in ["one_of_these", "all_of_these"]:
                value = condition['values']
            elif condition['value_type'] == "range":
                value = condition['values']
                
            formatted_condition = {
                "_id": ObjectId(),
                "conditionId": str(ObjectId()),
                "processId": "example_process_id",  # Replace with actual processId if available
                "type": condition['value_type'] if condition['value_type'] in ["all_of_these", "one_of_these", "range"] else "threshold",
                "field": condition['field'],
                "operator": condition['operator'],
                "value": value,
                "action": "require_approval_from_manager"  # Replace with actual action if available
            }
            formatted_conditions.append(formatted_condition)
    return formatted_conditions

def insert_into_mongodb(conditions):
    client = MongoClient('mongodb://localhost:27017/pdk')  # Replace with your MongoDB URI
    db = client['pdk']  # Replace with your database name
    collection = db['conditions']  # Replace with your collection name
    collection.insert_many(conditions)
    print(f"Inserted {len(conditions)} conditions into MongoDB")

# Main function
def main():
    num_conditions = int(input("Enter the number of conditions: "))
    
    conditions = []
    for i in range(num_conditions):
        condition_str = input(f"Enter condition {i+1}: ").strip()
        condition = parse_condition(condition_str)
        conditions.append(condition)
    
    grouped_conditions = group_conditions(conditions, num_conditions)
    formatted_conditions = format_for_mongodb(grouped_conditions)
    
    print("Extracted Conditions:")
    for condition in conditions:
        print(condition)
    
    print("Grouped Conditions for MongoDB Insertion:")
    for group in grouped_conditions:
        print(group)
    
    print("Formatted Conditions for MongoDB:")
    for condition in formatted_conditions:
        print(condition)
    
    # Insert formatted conditions into MongoDB
    insert_into_mongodb(formatted_conditions)

if __name__ == "__main__":
    main()
