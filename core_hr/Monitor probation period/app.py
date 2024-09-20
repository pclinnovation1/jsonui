from flask import Flask
from routes import calculator, about, home

app = Flask(__name__)

app.add_url_rule('/', 'home', home, methods=['GET', 'POST'])
app.add_url_rule('/about', 'about', about)

if __name__ == '__main__':
    app.run(debug=True)
