# import os

# class Config:
#     SECRET_KEY = os.environ.get('33cbfb8f083dd79b16ef4dcf9445968adfa74d6a03ca657e') or 'you-will-never-guess'
#     MONGO_URI = 'mongodb://localhost:27017/AF'
#     MAIL_SERVER = 'smtp.gmail.com'
#     MAIL_PORT = 587
#     MAIL_USE_TLS = True
#     MAIL_USERNAME = os.environ.get('piyushbirkh@gmail.com')  # Set this in your environment variables
#     MAIL_PASSWORD = os.environ.get('teaz yfbj jcie twrt')  # Set this in your environment variables




# import os

# class Config:
#     SECRET_KEY = os.environ.get('a13b6fe4a6b8df817a51dea222cbad9d78c5ac025b5680176d94c31bb06b0d6d') or 'you-will-never-guess'
#     MONGO_URI = os.environ.get('mongodb://localhost:27017/AF') or 'mongodb://localhost:27017/AF'
#     MAIL_SERVER = 'smtp.gmail.com'
#     MAIL_PORT = 587
#     MAIL_USE_TLS = True
#     MAIL_USERNAME = os.environ.get('pawan457maurya@gmail.com')
#     MAIL_PASSWORD = os.environ.get('kzch vddk klmd mutx')
    
   
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/AF'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'pawan457maurya@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'kzch vddk klmd mutx'
   
