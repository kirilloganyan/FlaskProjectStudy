import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-not-pass'
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/db_for_flask1"
    MAILADRESS = ['bestMail@example.com']
    OAUTH_CREDENTIALS = {
        'vk': {
            'id': '51692970',
            'secret': '62qHHzT7vqmqHrGTH0LX'
        }
    }