import os

class Config:
    SECRET_KEY = os.environ.get('33cbfb8f083dd79b16ef4dcf9445968adfa74d6a03ca657e') or 'you-will-never-guess'
    MONGO_URI = 'mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('piyushbirkh@gmail.com')
    MAIL_PASSWORD = os.environ.get('teaz yfbj jcie twrt')