
import openai
import pymongo
import json

# Set your OpenAI API key
openai.api_key = 'sk-proj-qzlQFOC6zv1JcMjpPAJWT3BlbkFJamSyI9QKpTg0WuQW3wSu'

# MongoDB connection setup
client = pymongo.MongoClient("mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns")
db = client["PCL_Interns"]
collection = db["conditions"]

def get_condition_input():
    num_conditions = int(input("Enter the number of conditions: "))
    process_name = input("Enter the process name: ")
    conditions = []
    for i in range(num_conditions):
        condition = input(f"Enter condition {i + 1}: ")
        nested = input(f"Is condition {i + 1} nested (N) or not nested (NN)?: ")
        condition_type = "nested" if nested.lower() == "n" else "not_nested"
        condition_operator = input("Enter the condition type operator (or, all, in, na): ")
        conditions.append((condition, condition_type, condition_operator))
    return process_name, conditions

def generate_mongodb_format(process_name, conditions):
    condition_strs = []
    for condition, condition_type, condition_operator in conditions:
        condition_strs.append(f"{condition} ({condition_type}, {condition_operator})")
    
    conditions_formatted = "\n".join(condition_strs)
    
    prompt = (
        "Convert the following conditions into a valid JSON format for MongoDB. "
        "Include nested conditions in the 'nestedConditions' array field if applicable:\n"
        f"Process Name: {process_name}\n"
        "Conditions:\n"
        f"{conditions_formatted}\n"
        "The JSON format should be:\n"
        "{\n"
        '  "processName": "<process_name>",\n'
        '  "conditions": [\n'
        '    {\n'
        '      "field": "<field>",\n'
        '      "operator": "<operator>",\n'
        '      "value": "<value>",\n'
        '      "nested": <true/false>,\n'
        '      "conditionType": "<condition_type>"\n'
        '    },\n'
        '    {\n'
        '      "conditionType": "<condition_type>",\n'
        '      "nestedConditions": [\n'
        '        {\n'
        '          "field": "<nested_field>",\n'
        '          "operator": "<nested_operator>",\n'
        '          "value": "<nested_value>"\n'
        '        }\n'
        '      ]\n'
        '    }\n'
        '  ]\n'
        '}'
    )
    
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content']

def extract_json_objects_from_response(response):
    try:
        response = response.strip()
        json_start_index = response.find('{')
        json_end_index = response.rfind('}') + 1
        if json_start_index == -1 or json_end_index == -1:
            print("No valid JSON found in the response.")
            return []

        json_str = response[json_start_index:json_end_index]
        return [json.loads(json_str)]
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    return []

def main():
    process_name, conditions = get_condition_input()
    formatted_conditions = generate_mongodb_format(process_name, conditions)
    print("Formatted Conditions:", formatted_conditions)
    
    formatted_conditions_list = extract_json_objects_from_response(formatted_conditions)
    
    if formatted_conditions_list:
        # Update MongoDB collection
        collection.insert_many(formatted_conditions_list)
        print("Conditions have been updated in the MongoDB collection.")
    else:
        print("Failed to format conditions correctly.")

if __name__ == "__main__":
    main()
