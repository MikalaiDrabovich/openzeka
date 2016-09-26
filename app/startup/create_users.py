"""
Open Zeka Image Recognition Web & API Server
This is pre release version
http://openzeka.com
http://github.com/ferhatkurt/openzeka

Based on Flask-user starter app
"""
from datetime import datetime
from app import app, db
# OpenZeka: added Usage
from app.core.models import User, Role, Usage
#OpenZeka
from app.core.views import add_months

def create_users():
    """ Create users when app starts """
    from app.core.models import User, Role

    # Create all tables
    db.create_all()

    # Adding roles
    admin_role = find_or_create_role('admin', u'Admin')

    # OpenZeka: Add users with username - admin, user
    user = find_or_create_user(u'1', u'admin', u'Admin', u'Example', u'admin@example.com', 'Password1', u'127.0.0.1', admin_role)
    user = find_or_create_user(u'2', u'user', u'User', u'Example', u'user@example.com', 'Password1', u'127.0.0.1')

    # Save to DB
    db.session.commit()


def find_or_create_role(name, label):
    """ Find existing role or create new role """
    role = Role.query.filter(Role.name == name).first()
    if not role:
        role = Role(name=name, label=label)
        db.session.add(role)
    return role

#OpenZeka: Added username,reg_ip field
def find_or_create_user(user_id, username, first_name, last_name, email, password, reg_ip, role=None):
    """ Find existing user or create new user """
    user = User.query.filter(User.email == email).first()
    if not user:
        user = User(username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=app.user_manager.hash_password(password),
                    active=True,
                    confirmed_at=datetime.utcnow(),
                    reg_ip = reg_ip)
        if role:
            user.roles.append(role)
        db.session.add(user)

        #OpenZeka: add user usage limit information
        i = datetime.now()
        usage_date = "%s,%s,%s" % (i.day, i.month, i.year)
        today = datetime.now()
        next_month = add_months(today, 1)
        item = Usage(
            user_id=user_id,
            # Adding 25000 limit for admin, user.
            usages=usage_date + "," + str(next_month[0]) + ',' + str(next_month[1]) + ',' + str(
                next_month[2]) + ",0,25000"
            # usages=usage_date + "," + str(next_month[0]) + ',' + str(next_month[1]) + ',' + str(
            #     next_month[2]) + ",0,25000;" + usage_date + "," + str(next_month[-1]) + ',' + str(next_month[0]) + ',' + str(
            #     next_month[2]) + ",18500,25000;"
        )
        db.session.add(item)
    return user