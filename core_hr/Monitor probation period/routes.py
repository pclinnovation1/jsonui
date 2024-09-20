from flask import render_template, request
from logic import process_request

def calculator():
    expression, result = '', ''
    if request.method == 'POST':
        expression, result = process_request(request)
    return render_template('index.html', expression=expression, result=result)

def about():
    return render_template('about.html')

def home():
    return calculator()
