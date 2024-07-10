

def get_field_value(approval_rules, field_name):
    for rule in approval_rules.get('rules', []):
        condition = rule.get('condition', {})
        if condition.get('field') == field_name:
            return condition.get('value')
        elif condition.get('nestedConditions'):
            for nested_condition in condition.get('nestedConditions'):
                if nested_condition.get('field') == field_name:
                    return nested_condition.get('value')
    return None

def evaluate_condition(field_types, field_values, condition, approval_rules):
    print("Field Types:", field_types)
    print("Field Values:", field_values)
    print("Condition:", condition)
    print("Approval Rules:", approval_rules)
    
    condition_type = condition.get('conditionType')
    print("Condition Type:", condition_type)

    if condition_type == 'na':
        # Simple condition evaluation
        nested_conditions = condition.get('nestedConditions', [])
        for nested in nested_conditions:
            field = nested.get('field')
            operator = nested.get('operator')
            value = nested.get('value')

            if field not in field_types:
                print(f"Field {field} not in provided field types")
                return False

            field_index = field_types.index(field)
            field_value = field_values[field_index]

            result = evaluate_single_condition(field_value, operator, value)
            print(f"Evaluated single condition: Field={field}, Operator={operator}, Value={value}, Result={result}")
            return result
    
    elif condition_type in ('all', 'or'):
        nested_conditions = condition.get('nestedConditions', [])
        results = []
        for nested in nested_conditions:
            field = nested.get('field')
            operator = nested.get('operator')
            value = nested.get('value')

            if field not in field_types:
                print(f"Field {field} not in provided field types")
                results.append(False)
                continue

            field_index = field_types.index(field)
            field_value = field_values[field_index]

            nested_result = evaluate_single_condition(field_value, operator, value)
            results.append(nested_result)
            print(f"Evaluated nested condition: Field={field}, Operator={operator}, Value={value}, Result={nested_result}")

        if condition_type == 'all':
            result = all(results)
            print(f"Evaluated 'all' condition with results {results}: Result={result}")
            if result:
                approver_list = [rule['approvers'] for rule in approval_rules['rules'] if rule['condition'] == condition]
                return approver_list[0] if approver_list else []
            return []
        elif condition_type == 'or':
            result = any(results)
            print(f"Evaluated 'or' condition with results {results}: Result={result}")
            if result:
                approver_list = [rule['approvers'] for rule in approval_rules['rules'] if rule['condition'] == condition]
                return approver_list[0] if approver_list else []
            return []

    return False

def evaluate_single_condition(field_value, operator, condition_value):
    print(f"Evaluating single condition: Field Value={field_value}, Operator={operator}, Condition Value={condition_value}")
    
    if operator == '<':
        result = field_value < condition_value
    elif operator == '>':
        result = field_value > condition_value
    elif operator == 'between':
        result = condition_value[0] <= field_value <= condition_value[1]
    elif operator == '==':
        result = field_value == condition_value
    elif operator == '!=':
        result = field_value != condition_value
    else:
        result = False

    print(f"Result of single condition evaluation: Field Value={field_value}, Operator={operator}, Condition Value={condition_value}, Result={result}")
    return result
