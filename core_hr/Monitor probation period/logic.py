from evaluator import evaluate_expression

def process_request(request):
    expression = request.form['expression']
    result = evaluate_expression(expression)
    return expression, result
