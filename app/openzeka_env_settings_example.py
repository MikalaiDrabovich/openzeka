"""
Open Zeka Image Recognition Web & API Server
This is pre release version
http://openzeka.com
http://github.com/ferhatkurt/openzeka

Based on Flask-user starter app
"""
import os

# *****************************
# Environment specific settings
# *****************************

# The settings below can (and should) be over-ruled by OS environment variable settings

# Flask settings                     # Generated with: import os; os.urandom(24)
SECRET_KEY = 'Jz\xa1\xdaW\xfc\xa8\xd8!z-S\x9d\xc5\x02>\xe3\xbc86\x11\x18\xc9\xb3'
# PLEASE USE A DIFFERENT KEY FOR PRODUCTION ENVIRONMENTS!

# SQLAlchemy Connection Settings
# Sqlite
SQLITE_DB_NAME = 'openzeka.sqlite'
# Do not change below URI addresses
SQLALCHEMY_DATABASE_URI = 'sqlite:///../' + SQLITE_DB_NAME
SQLALCHEMY_API_DATABASE_URI = 'sqlite:///' + SQLITE_DB_NAME

# PostgreSQL
# sample connection
# 'SQLALCHEMY_DATABASE_URI': 'postgresql+psycopg2://openpsql:username=>password@localhost:5432/opendb'
# 'SQLALCHEMY_API_DATABASE_URI': 'postgresql+psycopg2://openpsql:username=>password@localhost:5432/opendb'

# Flask-Mail settings
MAIL_USERNAME = 'email@example.com'
MAIL_PASSWORD = 'password'
MAIL_DEFAULT_SENDER = '"AppName" <noreply@example.com>'
MAIL_SERVER = 'MAIL_SERVER', 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USE_TLS = False


# Flask-Mail settings for sendgrid
# MAIL_USERNAME = 'username'
# MAIL_PASSWORD = 'password'
# MAIL_DEFAULT_SENDER = 'info@localhost'
# MAIL_SERVER = 'smtp.sendgrid.net'
# MAIL_PORT = 2525
# MAIL_USE_SSL = False
# MAIL_USE_TLS = False

# Unhandled exceptions will now send an email message to ADMINS.
# Change email address for get messages
ADMINS = [
    '"Open Zeka Admin" <info@localhost>',
    ]