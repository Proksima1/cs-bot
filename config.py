import os
if not os.path.exists('db'):
    os.mkdir('db')
SQLALCHEMY_DATABASE_URI = 'sqlite:///db/app.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'AbhksblfnahkfvayiG&!gogdjkaSOI9-jfas[j*ASg76afyfyi'
DEBUG = True