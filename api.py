# coding: utf-8
"""
Open Zeka Image Recognition Web & API Server
This is pre release version
http://openzeka.com
http://github.com/ferhatkurt/openzeka

Based on https://github.com/lepture/flask-oauthlib
"""
from datetime import datetime, timedelta
from flask import Flask, g, render_template, request, jsonify, make_response
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_oauthlib.provider import OAuth2Provider
from flask_oauthlib.contrib.oauth2 import bind_sqlalchemy
from flask_oauthlib.contrib.oauth2 import bind_cache_grant

# OpenZeka:
from flask_user import UserMixin
from flask_script import Manager

import calendar



# Image Classifier
import cStringIO as StringIO
import logging
import urllib
import caffe
import optparse
import os

from app.core.models import ImagenetClassifier_api
import werkzeug



# OpenZeka: Caffe Web Demo exutils.py defs
from app.core.views import open_oriented_im, apply_orientation

from flask.ext.reqarg import request_args

# OpenZeka:
app = Flask(__name__)           # The WSGI compliant web application object
db = SQLAlchemy(app)            # Setup Flask-SQLAlchemy


# OpenZeka: Config file can call with startup
app.config.from_object('app.startup.common_settings')
env_settings_file = os.environ.get('OPENZEKA_ENV_SETTINGS_FILE', 'app/openzeka_env_settings_example.py')
app.config.from_pyfile(env_settings_file)

app.debug = app.config['API_DEBUD']
app.secret_key = app.config['SECRET_KEY']
app.config.update({
    'SQLALCHEMY_DATABASE_URI': app.config['SQLALCHEMY_API_DATABASE_URI']
})
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information (required for Flask-User)
    # OpenZeka: Added username for registration
    username = db.Column(db.String(50), nullable=True, unique=True)
    email = db.Column(db.Unicode(255), nullable=False, server_default=u'', unique=True)
    confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')
    reset_password_token = db.Column(db.String(100), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='0')

    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')
    last_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')

    reg_ip = db.Column(db.Unicode(50), nullable=False, server_default=u'')

    # Relationships
    roles = db.relationship('Role', secondary='users_roles',
                            backref=db.backref('users', lazy='dynamic'))
    @property
    def username(self):
        if self.email:
            return self.email.split()
        return []

# User usage table
class Usage(db.Model):
    __tablename__ = 'usage'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.id'))
    usages = db.Column(db.String)
    user = db.relationship('User')

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, server_default=u'', unique=True)  # for @roles_accepted()
    label = db.Column(db.Unicode(255), server_default=u'')  # for display purposes


# Define the UserRoles association model
class UsersRoles(db.Model):
    __tablename__ = 'users_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

class Client(db.Model):
    # id = db.Column(db.Integer, primary_key=True)
    # human readable name
    # name = db.Column(db.String(40))
    __tablename__ = 'client'
    application_id = db.Column(db.Integer, nullable=False, primary_key=True)
    application_name = db.Column(db.Text)
    client_id = db.Column(db.String(40), unique=True, index=True,
                              nullable=False)
    client_secret = db.Column(db.String(55), unique=True, index=True,
                              nullable=False)
    client_type = db.Column(db.String(20), default='public')

    _redirect_uris = db.Column(db.Text)
    default_scope = db.Column(db.Text, default='api_access')

    user_id = db.Column(db.ForeignKey('users.id'))
    user = db.relationship('User')

    @property
    def user(self):
        return User.query.get(1)

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self.default_scope:
            return self.default_scope.split()
        return []

    @property
    def allowed_grant_types(self):
        return ['authorization_code', 'password', 'client_credentials',
                'refresh_token']


class Grant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')
    )
    user = relationship('User')

    client_id = db.Column(
        db.String(40), db.ForeignKey('client.client_id', ondelete='CASCADE'),
        nullable=False,
    )
    client = relationship('Client')
    code = db.Column(db.String(255), index=True, nullable=False)

    redirect_uri = db.Column(db.String(255))
    scope = db.Column(db.Text)
    expires = db.Column(db.DateTime)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self.scope:
            return self.scope.split()
        return None


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.String(40), db.ForeignKey('client.client_id', ondelete='CASCADE'),
        nullable=False,
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')
    )
    user = relationship('User')
    client = relationship('Client')
    token_type = db.Column(db.String(40))
    access_token = db.Column(db.String(255))
    refresh_token = db.Column(db.String(255))
    expires = db.Column(db.DateTime)
    scope = db.Column(db.Text)

    def __init__(self, **kwargs):
        expires_in = kwargs.pop('expires_in')
        self.expires = datetime.utcnow() + timedelta(seconds=expires_in)
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def scopes(self):
        if self.scope:
            return self.scope.split()
        return []

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self


def current_user():
    return g.user


def cache_provider(app):
    oauth = OAuth2Provider(app)

    bind_sqlalchemy(oauth, db.session, user=User,
                    token=Token, client=Client)

    app.config.update({'OAUTH2_CACHE_TYPE': 'simple'})
    bind_cache_grant(app, oauth, current_user)
    return oauth


def sqlalchemy_provider(app):
    oauth = OAuth2Provider(app)

    bind_sqlalchemy(oauth, db.session, user=User, token=Token,
                    client=Client, grant=Grant, current_user=current_user)

    return oauth


def default_provider(app):
    oauth = OAuth2Provider(app)

    @oauth.clientgetter
    def get_client(client_id):
        return Client.query.filter_by(client_id=client_id).first()

    @oauth.grantgetter
    def get_grant(client_id, code):
        return Grant.query.filter_by(client_id=client_id, code=code).first()

    @oauth.tokengetter
    def get_token(access_token=None, refresh_token=None):
        if access_token:
            return Token.query.filter_by(access_token=access_token).first()
        if refresh_token:
            return Token.query.filter_by(refresh_token=refresh_token).first()
        return None

    @oauth.grantsetter
    def set_grant(client_id, code, request, *args, **kwargs):
        expires = datetime.utcnow() + timedelta(seconds=100)
        grant = Grant(
            client_id=client_id,
            code=code['code'],
            redirect_uri=request.redirect_uri,
            scope=' '.join(request.scopes),
            user_id=g.user.id,
            expires=expires,
        )
        db.session.add(grant)
        db.session.commit()

    @oauth.tokensetter
    def set_token(token, request, *args, **kwargs):
        # In real project, a token is unique bound to user and client.
        # Which means, you don't need to create a token every time.
        tok = Token(**token)
        tok.user_id = request.client.user_id
        tok.client_id = request.client.client_id
        toks = Token.query.filter_by(
            client_id=tok.client_id
        )
        # make sure that every client has only one token connected to a user
        for t in toks:
            db.session.delete(t)

        db.session.add(tok)
        db.session.commit()

    @oauth.usergetter
    def get_user(username, password, *args, **kwargs):
        # This is optional, if you don't need password credential
        # there is no need to implement this method
        return User.query.filter_by(username=username).first()

    return oauth


def prepare_app(app):
    db.init_app(app)
    db.app = app
    db.create_all()
    return app


def create_server(app, oauth=None):
    if not oauth:
        oauth = default_provider(app)

    app = prepare_app(app)

    @app.before_request
    def load_current_user():
        user = User.query.get(1)
        g.user = user

    @app.route('/')
    def home():
        # return render_template('home.html')
        return "API is working. Please read documentation to access the API"

    @app.route('/oauth/authorize', methods=['GET', 'POST'])
    @oauth.authorize_handler
    def authorize(*args, **kwargs):
        # NOTICE: for real project, you need to require login
        if request.method == 'GET':
            # render a page for user to confirm the authorization
            return render_template('confirm.html')

        if request.method == 'HEAD':
            # if HEAD is supported properly, request parameters like
            # client_id should be validated the same way as for 'GET'
            response = make_response('', 200)
            response.headers['X-Client-ID'] = kwargs.get('client_id')
            return response

        confirm = request.form.get('confirm', 'no')
        return confirm == 'yes'

    @app.route('/oauth/token', methods=['POST', 'GET'])
    @oauth.token_handler
    def access_token():
        return {}

    @app.route('/oauth/revoke', methods=['POST'])
    @oauth.revoke_handler
    def revoke_token():
        pass

    @app.route('/api/email')
    @oauth.require_oauth('api_access')
    def email_api():
        oauth = request.oauth
        return jsonify(username=oauth.user.username)

    @app.route('/api/client')
    @oauth.require_oauth()
    def client_api():
        oauth = request.oauth
        return jsonify(client=oauth.user.username)

    @app.route('/api/address/<city>')
    # scope icinde address yer alirsa asagidan sonuc doner. Su anda sadece api_access tanimladik.
    @oauth.require_oauth('address')
    def address_api(city):
        oauth = request.oauth
        return jsonify(address=city, username=oauth.user.username)

    @app.route('/api/method', methods=['GET', 'POST', 'PUT', 'DELETE'])
    @oauth.require_oauth()
    def method_api():
        return jsonify(method=request.method)

    @app.route('/v1/tag', methods=['GET', 'POST'])
    # @oauth.require_oauth('api_access')
    @oauth.require_oauth()
    @request_args
    def image_api(url):
        oauth = request.oauth
        imageurl = url
        if 'imagefile' in request.files:
            imagefile = request.files['imagefile']
        else:
            imagefile = "bos"
        test = request.args.get('url', '')

        try:
            if imageurl:
                string_buffer = StringIO.StringIO(
                    urllib.urlopen(imageurl).read())
                image = caffe.io.load_image(string_buffer)
            elif imagefile:
                # filename_ = str(datetime.datetime.now()).replace(' ', '_') + \
                filename_ = str(datetime.now()).replace(' ', '_') + \
                            werkzeug.secure_filename(imagefile.filename)
                filename = os.path.join(app.config['UPLOAD_FOLDER'], filename_)
                imagefile.save(filename)
                logging.info('Saving to %s.', filename)
                image = open_oriented_im(filename)
            else:
                return jsonify(resim=imageurl, imagefile=imagefile)

        except Exception as err:
            # For any exception we encounter in reading the image, we will just
            # not continue.
            logging.info('URL Image open error: %s', err)
            # return jsonify(method=request.method, url=imageurl, test=test, imagefile=imagefile, error=err)
            return jsonify(error=err)
        logging.info('Image: %s', imageurl)
        result_deep = app.clf.classify_image(image)

        oauth = request.oauth
        usage_ = Usage.query.filter_by(user_id=oauth.user.id).first()

        if ';' in usage_.usages:
            # If user has months old and usage with (;)
            months_select = usage_.usages.rsplit(';',1)
            old_months_with_usage = months_select[0]+';'
            # Select latest month with usage
            last_month_with_usage = months_select[1]
            # Split latest month details as dates and usages - 19,5,2016,19,6,2016,3,5000 diveded 19,5,2016,19,6,2016 and 3 and 5000
            last_month_quota = last_month_with_usage.rsplit(',', 2)
            last_month_dates = last_month_quota[0]
            last_month_quota_usage = int(last_month_quota[1])
            last_month_quota_limit = last_month_quota[2]
        else:
            old_months_with_usage = ''
            last_month_quota = usage_.usages.rsplit(',', 2)
            last_month_dates = last_month_quota[0]
            last_month_quota_usage = int(last_month_quota[1])
            last_month_quota_limit = last_month_quota[2]
            # last_month_with_usage = usage_.usages.split(",")

        today = datetime.now()
        past_month = last_month_quota[0].split(',')
        past = datetime(int(past_month[5]), int(past_month[4]), int(past_month[3]))
        if(today>past):
            start_date = "%s,%s,%s" % (today.day, today.month, today.year)
            # start_date = datetime(int(latest_usage[2]), int(latest_usage[1]), int(latest_usage[0]))
            next_month = add_months(today, 1)
            # next_month = "1,9,2016"
            usage_.usages = usage_.usages+";"+start_date+","+str(next_month[0])+','+str(next_month[1])+','+str(next_month[2])+",1,25000"
            db.session.add(usage_)
            db.session.commit()
        else:
            # Increment quota usage
            last_month_quota_usage += 1
            # Remove latest month with usage details (this removes after latest (;) )
            # Add latest month with usage details
            usage_.usages = old_months_with_usage+last_month_dates+","+str(last_month_quota_usage)+","+last_month_quota_limit
            db.session.add(usage_)
            db.session.commit()
        # return jsonify({'status_code':'OK','status_message':'Tagged image'},results=result_deep)
        # For every image request below layer will extend
        result_object = [{'status_code': 'OK',
                          'status_message': 'OK',
                          'image': imageurl,
                          'result': result_deep}]

        object = {'Configuration':
                      {'app_name': oauth.client.application_name,
                       'model': 'Model v1',
                       'scopes': oauth.client.default_scope,
                       'usage': last_month_quota_usage,
                       'limit':last_month_quota_limit},
                  'Results': result_object}
        return jsonify(object)


    @oauth.invalid_response
    def require_oauth_invalid(req):
        return jsonify(message=req.error_message), 401


    return app

# Adding month to usage
# http://stackoverflow.com/questions/4130922/how-to-increment-datetime-by-custom-months-in-python-without-using-library
def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12)
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return (day,month,year)

if __name__ == '__main__':
    app = create_server(app)

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    parser = optparse.OptionParser()
    parser.add_option(
        '-r', '--reload',
        help="enable reload mode",
        action="store_true", default=False)
    parser.add_option(
        '-d', '--debug',
        help="enable debug mode",
        action="store_true", default=False)
    parser.add_option(
        '-p', '--port',
        help="which port to serve content on",
        type='int', default=9000)
    parser.add_option(
        '-g', '--gpu',
        help="use gpu mode",
        action='store_true', default=False)

    opts, args = parser.parse_args()
    ImagenetClassifier_api.default_args.update({'gpu_mode': opts.gpu})

    # Initialize classifier + warm start by forward for allocation
    app.clf = ImagenetClassifier_api(**ImagenetClassifier_api.default_args)
    app.clf.net.forward()
    if opts.debug:
        app.run(debug=True, host='0.0.0.0', port=opts.port)
    else:
        app.run(host='0.0.0.0', port=opts.port)