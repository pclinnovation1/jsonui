# from pymongo import MongoClient

# # Connect to MongoDB
# def connect_to_mongodb():
#     client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
#     db = client['PCL_Interns']
#     collection = db['Performance_Data']
#     return db, collection

# # Fetch all goal plans from MongoDB
# def fetch_all_goal_plans(collection):
#     return collection.find()

# # Convert percentage strings or numbers to float, handling percentage and absolute values
# def parse_value(value):
#     if isinstance(value, str):
#         if '%' in value:
#             return float(value.strip('%')), True
#         elif value.lower() in ['tbd', 'yes', 'no', 'yes/no']:
#             return 0.0, False
#     try:
#         return float(value), False
#     except ValueError:
#         return 0.0, False

# # Calculate the estimated target result percentage using the given formula
# def calculate_estimated_target_result_percent(min_val, target_val, max_val, estimated_result):
#     if min_val < target_val:
#         if estimated_result < min_val:
#             return 0
#         elif estimated_result < target_val:
#             return ((estimated_result - min_val) / (target_val - min_val)) * 0.5 if target_val != min_val else 0
#         else:
#             return ((estimated_result - target_val) / (max_val - target_val) + 1) * 0.5 if max_val != target_val else 0
#     else:
#         if estimated_result > min_val:
#             return 0
#         elif estimated_result > target_val:
#             return ((estimated_result - min_val) / (target_val - min_val)) * 0.5 if target_val != min_val else 0
#         else:
#             return ((estimated_result - target_val) / (max_val - target_val) + 1) * 0.5 if max_val != target_val else 0

# # Calculate performance from data
# def calculate_performance(goals, max_bonus, annual_overall_salary):
#     total_performance = 0
#     final_bonus_amount = 0
#     results = []
#     for goal in goals:
#         weight, _ = parse_value(goal['weight'])
#         weight /= 100  # Ensure weight is in percentage terms
#         estimated_result = goal.get('estimated_result', goal.get('estimated_result_percent'))
#         estimated_result_value, is_est_percentage = parse_value(estimated_result)
#         max_val, _ = parse_value(goal.get('max', goal.get('max_percent')))
#         min_val, _ = parse_value(goal.get('min', goal.get('min_percent')))
#         target_val, _ = parse_value(goal.get('target', goal.get('target_percent')))

#         # Convert values to actual percentages if they were percentages
#         if is_est_percentage:
#             min_val /= 100
#             target_val /= 100
#             max_val /= 100
#             estimated_result_value /= 100

#         target_result_percent = calculate_estimated_target_result_percent(min_val, target_val, max_val, estimated_result_value)
        
#         weighted_target_result_percent = weight * target_result_percent
#         total_performance += weighted_target_result_percent

#         # Calculate amount
#         amount = ((weight * max_bonus * target_result_percent) / 100) * annual_overall_salary
#         final_bonus_amount += amount

#         results.append({
#             'Goal': goal['name'],
#             'Weight': goal['weight'],
#             'Target': goal.get('target', goal.get('target_percent')),
#             'Min': goal.get('min', goal.get('min_percent')),
#             'Max': goal.get('max', goal.get('max_percent')),
#             'Estimated Result': goal.get('estimated_result', goal.get('estimated_result_percent')),
#             'Estimated Target Result %': f"{target_result_percent * 100:.2f}%",
#             'Estimated Target Result Weighted %': f"{weighted_target_result_percent * 100:.2f}%",
#             'Amount': f"{amount:.2f}"
#         })

#     return total_performance, results, final_bonus_amount

# # Store results in MongoDB
# def store_results(db, plan_name, full_year_results, half_year_results, final_results):
#     collection = db['Performance_Result']
    
#     document = {
#         "goal_plan_name": plan_name,
#         "full_year_performance": {
#             "performance_percentage": f"{full_year_results['performance'] * 100:.2f}%",
#             "results": full_year_results['results'],
#             "bonus_amount": f"{full_year_results['bonus']:.2f}"
#         }
#     }

#     if half_year_results['H1']['performance'] != 0 or half_year_results['H2']['performance'] != 0:
#         document["half_year_performance"] = {
#             "H1": {
#                 "performance_percentage": f"{half_year_results['H1']['performance'] * 100:.2f}%",
#                 "results": half_year_results['H1']['results'],
#                 "bonus_amount": f"{half_year_results['H1']['bonus']:.2f}"
#             },
#             "H2": {
#                 "performance_percentage": f"{half_year_results['H2']['performance'] * 100:.2f}%",
#                 "results": half_year_results['H2']['results'],
#                 "bonus_amount": f"{half_year_results['H2']['bonus']:.2f}"
#             }
#         }

#         document["final_performance"] = {
#             "total_performance_percentage": f"{final_results['performance'] * 100:.2f}%",
#             "results": final_results['results'],
#             "final_bonus_amount": f"{final_results['bonus']:.2f}"
#         }

#     collection.insert_one(document)


# # Main function
# def main():
#     db, collection = connect_to_mongodb()
#     goal_plans = fetch_all_goal_plans(collection)

#     for goal_data in goal_plans:
#         plan_name = goal_data.get("goal_plan_name", "Unnamed Plan")

#         # Fetch max_bonus and annual_overall_salary from the data
#         max_bonus, _ = parse_value(goal_data.get('max_bonus_percent', '0%'))
#         annual_overall_salary = float(goal_data.get('annual_overall_salary', 0))

#         total_performance = 0
#         final_bonus_amount = 0
#         all_results = []

#         full_year_results = {'performance': 0, 'results': [], 'bonus': 0}
#         half_year_results = {'H1': {'performance': 0, 'results': [], 'bonus': 0}, 'H2': {'performance': 0, 'results': [], 'bonus': 0}}
#         final_results = {'performance': 0, 'results': [], 'bonus': 0}

#         if 'full_year_goals' in goal_data:
#             full_year_results['performance'], full_year_results['results'], full_year_results['bonus'] = calculate_performance(
#                 goal_data['full_year_goals'], max_bonus, annual_overall_salary)
#             total_performance += full_year_results['performance']
#             final_bonus_amount += full_year_results['bonus']
#             all_results.extend(full_year_results['results'])

#         if 'half_year_goals' in goal_data:
#             for half_year, goals in goal_data['half_year_goals'].items():
#                 half_year_results[half_year]['performance'], half_year_results[half_year]['results'], half_year_results[half_year]['bonus'] = calculate_performance(
#                     goals, max_bonus / 2, annual_overall_salary / 2)
#                 total_performance += half_year_results[half_year]['performance']
#                 final_bonus_amount += half_year_results[half_year]['bonus']
#                 all_results.extend(half_year_results[half_year]['results'])

#         final_results['performance'] = total_performance
#         final_results['results'] = all_results
#         final_results['bonus'] = final_bonus_amount

#         store_results(db, plan_name, full_year_results, half_year_results, final_results)

# if __name__ == "__main__":
#     main()






























from pymongo import MongoClient

# Connect to MongoDB
def connect_to_mongodb():
    client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
    db = client['PCL_Interns']
    collection = db['Performance_Data']
    return db, collection

# Fetch all goal plans from MongoDB
def fetch_all_goal_plans(collection):
    return collection.find()

# Convert percentage strings or numbers to float, handling percentage and absolute values
def parse_value(value):
    if isinstance(value, str):
        if '%' in value:
            return float(value.strip('%')), True
        elif value.lower() == 'tbd':
            return 0.0, False
        elif value.lower() == 'yes':
            return 100.0, True
        elif value.lower() == 'no':
            return 0.0, True
    try:
        return float(value), False
    except ValueError:
        return 0.0, False

# Calculate the estimated target result percentage using the given formula
def calculate_estimated_target_result_percent(min_val, target_val, max_val, estimated_result):
    if min_val < target_val:
        if estimated_result < min_val:
            return 0
        elif estimated_result < target_val:
            return ((estimated_result - min_val) / (target_val - min_val)) * 0.5 if target_val != min_val else 0
        else:
            return ((estimated_result - target_val) / (max_val - target_val) + 1) * 0.5 if max_val != target_val else 0
    else:
        if estimated_result > min_val:
            return 0
        elif estimated_result > target_val:
            return ((estimated_result - min_val) / (target_val - min_val)) * 0.5 if target_val != min_val else 0
        else:
            return ((estimated_result - target_val) / (max_val - target_val) + 1) * 0.5 if max_val != target_val else 0

# Calculate performance from data
def calculate_performance(goals, max_bonus, annual_overall_salary):
    total_performance = 0
    final_bonus_amount = 0
    results = []
    for goal in goals:
        weight, _ = parse_value(goal['weight'])
        weight /= 100  # Ensure weight is in percentage terms
        estimated_result = goal.get('estimated_result', goal.get('estimated_result_percent'))
        estimated_result_value, is_est_percentage = parse_value(estimated_result)
        max_val, _ = parse_value(goal.get('max', goal.get('max_percent')))
        min_val, _ = parse_value(goal.get('min', goal.get('min_percent')))
        target_val, _ = parse_value(goal.get('target', goal.get('target_percent')))

        # Convert values to actual percentages if they were percentages
        if is_est_percentage:
            min_val /= 100
            target_val /= 100
            max_val /= 100
            estimated_result_value /= 100

        target_result_percent = calculate_estimated_target_result_percent(min_val, target_val, max_val, estimated_result_value)
        
        weighted_target_result_percent = weight * target_result_percent
        total_performance += weighted_target_result_percent

        # Calculate amount
        amount = ((weight * max_bonus * target_result_percent) / 100) * annual_overall_salary
        final_bonus_amount += amount

        results.append({
            'Goal': goal['name'],
            'Weight': goal['weight'],
            'Target': goal.get('target', goal.get('target_percent')),
            'Min': goal.get('min', goal.get('min_percent')),
            'Max': goal.get('max', goal.get('max_percent')),
            'Estimated Result': goal.get('estimated_result', goal.get('estimated_result_percent')),
            'Estimated Target Result %': f"{target_result_percent * 100:.2f}%",
            'Estimated Target Result Weighted %': f"{weighted_target_result_percent * 100:.2f}%",
            'Amount': f"{amount:.2f}"
        })

    return total_performance, results, final_bonus_amount

# Store results in MongoDB
def store_results(db, plan_name, full_year_results, half_year_results, final_results):
    collection = db['Performance_Result']
    
    document = {
        "goal_plan_name": plan_name,
        "full_year_performance": {
            "performance_percentage": f"{full_year_results['performance'] * 100:.2f}%",
            "results": full_year_results['results'],
            "bonus_amount": f"{full_year_results['bonus']:.2f}"
        }
    }

    if half_year_results['H1']['performance'] != 0 or half_year_results['H2']['performance'] != 0:
        document["half_year_performance"] = {
            "H1": {
                "performance_percentage": f"{half_year_results['H1']['performance'] * 100:.2f}%",
                "results": half_year_results['H1']['results'],
                "bonus_amount": f"{half_year_results['H1']['bonus']:.2f}"
            },
            "H2": {
                "performance_percentage": f"{half_year_results['H2']['performance'] * 100:.2f}%",
                "results": half_year_results['H2']['results'],
                "bonus_amount": f"{half_year_results['H2']['bonus']:.2f}"
            }
        }

        document["final_performance"] = {
            "total_performance_percentage": f"{final_results['performance'] * 100:.2f}%",
            "results": final_results['results'],
            "final_bonus_amount": f"{final_results['bonus']:.2f}"
        }

    collection.insert_one(document)

# Main function
def main():
    db, collection = connect_to_mongodb()
    goal_plans = fetch_all_goal_plans(collection)

    for goal_data in goal_plans:
        plan_name = goal_data.get("goal_plan_name", "Unnamed Plan")

        # Fetch max_bonus and annual_overall_salary from the data
        max_bonus, _ = parse_value(goal_data.get('max_bonus_percent', '0%'))
        annual_overall_salary = float(goal_data.get('annual_overall_salary', 0))

        total_performance = 0
        final_bonus_amount = 0
        all_results = []

        full_year_results = {'performance': 0, 'results': [], 'bonus': 0}
        half_year_results = {'H1': {'performance': 0, 'results': [], 'bonus': 0}, 'H2': {'performance': 0, 'results': [], 'bonus': 0}}
        final_results = {'performance': 0, 'results': [], 'bonus': 0}

        if 'full_year_goals' in goal_data:
            full_year_results['performance'], full_year_results['results'], full_year_results['bonus'] = calculate_performance(
                goal_data['full_year_goals'], max_bonus, annual_overall_salary)
            total_performance += full_year_results['performance']
            final_bonus_amount += full_year_results['bonus']
            all_results.extend(full_year_results['results'])

        if 'half_year_goals' in goal_data:
            for half_year, goals in goal_data['half_year_goals'].items():
                half_year_results[half_year]['performance'], half_year_results[half_year]['results'], half_year_results[half_year]['bonus'] = calculate_performance(
                    goals, max_bonus / 2, annual_overall_salary / 2)
                total_performance += half_year_results[half_year]['performance']
                final_bonus_amount += half_year_results[half_year]['bonus']
                all_results.extend(half_year_results[half_year]['results'])

        final_results['performance'] = total_performance
        final_results['results'] = all_results
        final_results['bonus'] = final_bonus_amount

        store_results(db, plan_name, full_year_results, half_year_results, final_results)

if __name__ == "__main__":
    main()
