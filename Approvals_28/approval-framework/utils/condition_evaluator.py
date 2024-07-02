# utils/condition_evaluator.py
def evaluate_condition(value, condition):
    print("Evaluating condition:", condition)
    operator = condition['operator']
    condition_value = condition['value']
    
    print(f"Evaluating {value} with operator {operator} and value {condition_value}")

    if operator == '<':
        return value < condition_value
    elif operator == '>':
        return value > condition_value
    elif operator == 'between':
        return condition_value[0] <= value <= condition_value[1]
    elif operator == '==':
        return value == condition_value
    elif operator == '!=':
        return value != condition_value
    return False
