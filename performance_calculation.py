# import pdfplumber
# import numpy as np
# from fpdf import FPDF

# pdf_path = r"C:\Users\DELL\Desktop\MongoDB\performance_evaluation\sample_performance_report.pdf"

# def extract_data_from_pdf(pdf_path):
#     with pdfplumber.open(pdf_path) as pdf:
#         text = ''
#         for page in pdf.pages:
#             text += page.extract_text() + '\n'

#     data = {
#         'goals': [],
#         'competencies': [],
#         'feedback_scores': []
#     }

#     lines = text.split('\n')
#     current_goal = {}
#     current_competency = {}
    
#     for line in lines:
#         line = line.strip()  # Remove any leading/trailing whitespace
#         if ':' in line:
#             key, value = line.split(':', 1)
#             key = key.strip()
#             value = value.strip()
            
#             if key.startswith('Goal'):
#                 if current_goal:
#                     data['goals'].append(current_goal)
#                     current_goal = {}
#                 current_goal['name'] = value
#             elif key == 'Weight' and 'Competency' not in current_goal:
#                 current_goal['weight'] = float(value)
#             elif key == 'Target':
#                 current_goal['target'] = float(value)
#             elif key == 'Actual':
#                 try:
#                     current_goal['actual'] = float(value)
#                 except ValueError:
#                     current_goal['actual'] = 0.0  # Default value if parsing fails
#             elif key == 'Start Date':
#                 current_goal['start_date'] = value
#             elif key == 'End Date':
#                 current_goal['end_date'] = value
#             elif key == 'Completion Date':
#                 current_goal['completion_date'] = value
#             elif key == 'Status':
#                 current_goal['status'] = value
#             elif key.startswith('Competency'):
#                 if current_competency:
#                     data['competencies'].append(current_competency)
#                     current_competency = {}
#                 current_competency['name'] = value
#             elif key == 'Weight' and 'Competency' in current_competency:
#                 current_competency['weight'] = float(value)
#             elif key == 'Rating':
#                 current_competency['rating'] = float(value)
#             elif 'Feedback Score' in key:
#                 try:
#                     data['feedback_scores'].append(float(value))
#                 except ValueError:
#                     data['feedback_scores'].append(0.0)  # Default value if parsing fails
    
#     if current_goal:
#         data['goals'].append(current_goal)
#     if current_competency:
#         data['competencies'].append(current_competency)

#     return data

# def calculate_goal_score(goals):
#     total_weight = sum(goal.get('weight', 0) for goal in goals)
#     if total_weight == 0:
#         return 0
#     score = sum((goal.get('actual', 0) / goal.get('target', 1)) * goal.get('weight', 0) for goal in goals)
#     return score / total_weight * 100

# def calculate_competency_score(competencies):
#     total_weight = sum(comp.get('weight', 0) for comp in competencies)
#     if total_weight == 0:
#         return 0
#     score = sum(comp.get('rating', 0) * comp.get('weight', 0) for comp in competencies)
#     return score / total_weight

# def calculate_feedback_score(feedback_scores):
#     if not feedback_scores:
#         return 0
#     return np.mean(feedback_scores)

# def calculate_overall_score(goal_score, competency_score, feedback_score, weights):
#     overall_score = (goal_score * weights['goals'] +
#                      competency_score * weights['competencies'] +
#                      feedback_score * weights['feedback'])
#     return overall_score

# def generate_performance_report(output_path, overall_score, goal_score, competency_score, feedback_score, recommendation):
#     pdf = FPDF()
#     pdf.add_page()

#     pdf.set_font('Arial', 'B', 16)
#     pdf.cell(0, 10, 'Performance Evaluation Report', 0, 1, 'C')

#     pdf.set_font('Arial', 'B', 12)
#     pdf.cell(0, 10, 'Overall Performance Score', 0, 1)
#     pdf.set_font('Arial', '', 12)
#     pdf.cell(0, 10, f'{overall_score:.2f}', 0, 1)

#     pdf.set_font('Arial', 'B', 12)
#     pdf.cell(0, 10, 'Goal Score', 0, 1)
#     pdf.set_font('Arial', '', 12)
#     pdf.cell(0, 10, f'{goal_score:.2f}', 0, 1)

#     pdf.set_font('Arial', 'B', 12)
#     pdf.cell(0, 10, 'Competency Score', 0, 1)
#     pdf.set_font('Arial', '', 12)
#     pdf.cell(0, 10, f'{competency_score:.2f}', 0, 1)

#     pdf.set_font('Arial', 'B', 12)
#     pdf.cell(0, 10, 'Feedback Score', 0, 1)
#     pdf.set_font('Arial', '', 12)
#     pdf.cell(0, 10, f'{feedback_score:.2f}', 0, 1)

#     pdf.set_font('Arial', 'B', 12)
#     pdf.cell(0, 10, 'Recommendation', 0, 1)
#     pdf.set_font('Arial', '', 12)
#     pdf.multi_cell(0, 10, recommendation)

#     pdf.output(output_path)

# weights = {
#     'goals': 0.5,
#     'competencies': 0.3,
#     'feedback': 0.2
# }

# extracted_data = extract_data_from_pdf(pdf_path)
# goals = extracted_data['goals']
# competencies = extracted_data['competencies']
# feedback_scores = extracted_data['feedback_scores']

# goal_score = calculate_goal_score(goals)
# competency_score = calculate_competency_score(competencies)
# feedback_score = calculate_feedback_score(feedback_scores)

# overall_score = calculate_overall_score(goal_score, competency_score, feedback_score, weights)

# if overall_score >= 90:
#     recommendation = "Performance Level: Outstanding\nRecommendation: Consider for leadership roles and advanced projects."
# elif 75 <= overall_score < 90:
#     recommendation = "Performance Level: Meets Expectations\nRecommendation: Continue current role with targeted development in specific areas."
# else:
#     recommendation = "Performance Level: Needs Improvement\nRecommendation: Implement a detailed development plan and provide additional support."

# output_pdf_path = r"C:\Users\DELL\Desktop\MongoDB\performance_evaluation\performance_report.pdf"
# generate_performance_report(output_pdf_path, overall_score, goal_score, competency_score, feedback_score, recommendation)

# print(f"Performance report generated and saved to: {output_pdf_path}")
























# def calculate_estimated_target_result_percent(estimated_result, target, min_val, max_val):
#     if estimated_result < min_val:
#         if estimated_result > max_val:
#             return 0
#         elif estimated_result > target:
#             return (estimated_result - min_val) / (target - min_val) * 0.5
#         else:
#             return ((estimated_result - target) / (max_val - target) + 1) * 0.5
#     else:
#         if estimated_result < min_val:
#             return 0
#         elif estimated_result < target:
#             return (estimated_result - min_val) / (target - min_val) * 0.5
#         else:
#             return ((estimated_result - target) / (max_val - target) + 1) * 0.5

# def calculate_performance(data):
#     total_performance = 0
#     for item in data:
#         # Calculate the estimated target result percentage
#         target_result_percent = calculate_estimated_target_result_percent(
#             item['Estimated_Result'], item['Target'], item['Min'], item['Max']
#         )
        
#         # Calculate weighted target result percentage
#         weighted_target_result_percent = item['Weight'] * target_result_percent
        
#         # Add to total performance
#         total_performance += weighted_target_result_percent
        
#         # You might want to store or print individual results
#         print(f"Target: {item['Name']}, Target Result %: {target_result_percent:.2f}, Weighted Result %: {weighted_target_result_percent:.2f}")
        
#     return total_performance

# # Example data
# targets = [
#     {"Name": "Group Net Sales (M€)", "Weight": 0.35, "Target": 190, "Min": 180, "Max": 200, "Estimated_Result": 200},
#     {"Name": "Group operative Ebit (M€)", "Weight": 0.35, "Target": 7.00, "Min": 5.50, "Max": 8.50, "Estimated_Result": 7.00},
#     # Add more targets as needed
# ]

# total_performance = calculate_performance(targets)
# print(f"Total Performance: {total_performance:.2f}%")







from pymongo import MongoClient

# Connect to MongoDB
def connect_to_mongodb():
    client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
    db = client['PCL_Interns']  # Connect to the correct database
    collection = db['Performance_Data']  # Connect to the correct collection
    return collection

# Fetch data from MongoDB
def fetch_data(collection, plan_name):
    document = collection.find_one({"goal_plan_name": plan_name})
    return document['goals'] if document and 'goals' in document else []

# Convert percentage strings or numbers to float
def parse_percentage(value):
    if isinstance(value, str) and '%' in value:
        return float(value.strip('%')) / 100
    else:
        return float(value)

# Calculate the estimated target result percentage
def calculate_estimated_target_result_percent(estimated_result, target_val, min_val, max_val):
    if estimated_result < min_val or estimated_result > max_val:
        return 0  # Out of bounds
    if estimated_result >= min_val and estimated_result <= target_val:
        return (estimated_result - min_val) / (target_val - min_val)
    if estimated_result > target_val and estimated_result <= max_val:
        return (max_val - estimated_result) / (max_val - target_val)

# Calculate performance from data
def calculate_performance(goals):
    total_performance = 0
    results = []
    for goal in goals:
        weight = parse_percentage(goal['weight'])
        estimated_result = parse_percentage(goal['estimated_result'])
        max_val = parse_percentage(goal['max_value'])
        min_val = parse_percentage(goal['min_value'])
        target_val = parse_percentage(goal['target_value'])

        target_result_percent = calculate_estimated_target_result_percent(estimated_result, target_val, min_val, max_val)
        print('target_result_percent',target_result_percent)

        weighted_target_result_percent = weight * target_result_percent
        total_performance += weighted_target_result_percent

        results.append({
            'Goal': goal['name'],
            'Target Result %': f"{target_result_percent * 100:.2f}%",
            'Weighted Result %': f"{weighted_target_result_percent * 100:.2f}%"
        })

    return total_performance, results

# Main function
def main():
    collection = connect_to_mongodb()
    goal_data = fetch_data(collection, "Annual Performance Goals 2024")
    if goal_data:
        total_performance, results = calculate_performance(goal_data)
        for result in results:
            print(f"{result['Goal']}: Target Result %: {result['Target Result %']}, Weighted Result %: {result['Weighted Result %']}")
        print(f"Total Performance: {total_performance * 100:.2f}%")
    else:
        print("No data found for the specified goal plan.")

if __name__ == "__main__":
    main()
