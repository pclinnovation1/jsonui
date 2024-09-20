import re
import math  # Added

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return 'Error'  # Handle division by zero
    return a / b

def modulo(a, b):
    return a % b

def reciprocal(a):  # Added
    if a == 0:
        return 'Error'  # Handle division by zero
    return 1 / a

def square(a):  # Added
    return a * a

def sqrt(a):  # Added
    if a < 0:
        return 'Error'  # Handle square root of negative number
    return math.sqrt(a)

def evaluate_expression(expression):
    try:
        # Define supported operators
        ops = {
            '+': add,
            '-': subtract,
            '*': multiply,
            '/': divide,
            '%': modulo,
            'reciprocal': reciprocal,  # Added
            'square': square,          # Added
            'sqrt': sqrt               # Added
        }

        # Tokenize the expression using regular expressions
        tokens = re.findall(r'\d+\.?\d*|[+\-*/%]|reciprocal|square|sqrt', expression)  # Modified

        if not tokens or len(tokens) == 1:
            return 'Error'

        # Validate the expression
        for i in range(len(tokens) - 1):
            if tokens[i] in ops and tokens[i + 1] in ops:
                return 'Error'

        # Evaluate the expression
        stack = []
        current_op = None

        for token in tokens:
            if token in ops:
                if token in ['reciprocal', 'square', 'sqrt']:  # Added check
                    # Unary operators
                    a = stack.pop()
                    stack.append(ops[token](a))
                else:
                    current_op = ops[token]
            else:
                if current_op:
                    stack[-1] = current_op(stack[-1], float(token))
                    current_op = None
                else:
                    stack.append(float(token))

        return str(stack[0]) if stack else 'Error'
    except Exception as e:
        return 'Error'
