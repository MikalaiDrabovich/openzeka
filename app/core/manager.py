"""
Open Zeka Image Recognition Web & API Server
This is pre release version
http://openzeka.com
http://github.com/ferhatkurt/openzeka

Based on Flask-user starter app
"""

from app import manager


@manager.command
def init_db():
    from app.startup.create_users import create_users

    create_users()