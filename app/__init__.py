# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.

from flask import Flask
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)           # The WSGI compliant web application object
db = SQLAlchemy(app)            # Setup Flask-SQLAlchemy
manager = Manager(app)          # Setup Flask-Script

from app.startup.create_app import create_app

# OpenZeka: Flask
# from flask_debugtoolbar import DebugToolbarExtension
# # the toolbar is only enabled in debug mode:
# app.debug = True
#
# # set a 'SECRET_KEY' to enable the Flask session cookies
# app.config['SECRET_KEY'] = '<replace with a secret key>'
# toolbar = DebugToolbarExtension(app)
# # toolbar