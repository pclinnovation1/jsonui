def evaluate_condition(field_types, field_values, condition):
    print("Field Types:", field_types)
    print("Field Values:", field_values)
    print("Condition:", condition)

    condition_type = condition.get('conditionType')
    print("Condition Type:", condition_type)

    if condition_type in ('all', 'or', 'in'):
        nested_conditions = condition.get('nestedConditions', [])
        results = []
        for nested in nested_conditions:
            field = nested.get('field')
            operator = nested.get('operator')
            value = nested.get('value')
            if field in field_types:
                field_value = field_values[field_types.index(field)]
                result = evaluate_single_condition_logic(field_value, operator, value)
                results.append(result)
            else:
                results.append(False)
            print(f"Nested Condition: Field={field}, Operator={operator}, Value={value}, Result={results[-1]}")
        
        if condition_type == 'all':
            return all(results)
        elif condition_type == 'or' or condition_type == 'in':
            return any(results)
    elif condition_type == 'na':
        field = condition.get('field')
        operator = condition.get('operator')
        value = condition.get('value')
        if field in field_types:
            field_value = field_values[field_types.index(field)]
            return evaluate_single_condition_logic(field_value, operator, value)
        else:
            return False

    return False

def evaluate_single_condition_logic(field_value, operator, condition_value):
    print(f"Evaluating single condition: Field Value={field_value}, Operator={operator}, Condition Value={condition_value}")

    if isinstance(condition_value, bool):
        field_value = field_value.lower() == 'true' if isinstance(field_value, str) else bool(field_value)
    elif isinstance(condition_value, int):
        field_value = int(field_value)
    elif isinstance(condition_value, float):
        field_value = float(field_value)
    
    if operator == '<':
        result = field_value < condition_value
    elif operator == '>':
        result = field_value > condition_value
    elif operator == '<=':
        result = field_value <= condition_value
    elif operator == '>=':
        result = field_value >= condition_value
    elif operator == 'between':
        result = condition_value[0] <= field_value <= condition_value[1]
    elif operator == '==':
        result = field_value == condition_value
    elif operator == '!=':
        result = field_value != condition_value
    elif operator == 'in':
        if isinstance(field_value, list):
            print(f"Checking if any of {field_value} are in {condition_value}")
            result = any(val in condition_value for val in field_value)
        else:
            result = field_value in condition_value
    else:
        result = False

    print(f"Result of single condition evaluation: Field Value={field_value}, Operator={operator}, Condition Value={condition_value}, Result={result}")
    return result

# field_types_4 = ['skills']
# field_values_4 = [['Leadership', 'Project Management']]
# condition_4 = {'conditionType': 'in', 'nestedConditions': [{'field': 'skills', 'operator': 'in', 'value': ['Leadership', 'Project Management']}]}

# result_4 = evaluate_condition(field_types_4, field_values_4, condition_4)
# print("Test Case 4 Result:", result_4)



# # Test Case 2
# field_types_2 = ['performance_rating']
# field_values_2 = [4]
# condition_2 = {'field': 'performance_rating', 'operator': '>=', 'value': 4, 'nested': False, 'conditionType': 'na'}

# result_2 = evaluate_condition(field_types_2, field_values_2, condition_2)
# print("Test Case 2 Result:", result_2)



# field_types_1 = ['job_opening']
# field_values_1 = ['true']
# condition_1 = {'field': 'job_opening', 'operator': '==', 'value': True, 'nested': False, 'conditionType': 'na'}

# result_1 = evaluate_condition(field_types_1, field_values_1, condition_1)
# print("Test Case 1 Result:", result_1)




# field_types_3 = ['qualification', 'years_in_current_role']
# field_values_3 = ['MBA', 3]
# condition_3 = {'conditionType': 'or', 'nestedConditions': [{'field': 'qualification', 'operator': '==', 'value': 'MBA'}, {'field': 'years_in_current_role', 'operator': '>=', 'value': 2}]}

# result_3 = evaluate_condition(field_types_3, field_values_3, condition_3)
# print("Test Case 3 Result:", result_3)















