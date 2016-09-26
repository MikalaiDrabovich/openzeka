# coding: utf-8
"""
Open Zeka Image Recognition Web & API Server
This is pre release version
http://openzeka.com
http://github.com/ferhatkurt/openzeka

Based on Flask-user starter app
"""

from flask_user import UserMixin
from flask_user.forms import RegisterForm
from flask_wtf import Form
# OpenZeka: added BooleanField, FileField
from wtforms import StringField, SubmitField, validators, BooleanField, PasswordField, FileField
from app import db, app

# OpenZeka:
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

# OpenZeka: Caffe
# caffe
import os
import caffe
import numpy as np
import pandas as pd
import logging
import cPickle
import time

# OpenZeka: Config file can call with startup
app.config.from_object('app.startup.common_settings')

# Define the User data model. Make sure to add the flask_user.UserMixin !!
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

    #OpenZeka: Added for collect reg
    reg_ip = db.Column(db.Unicode(50), nullable=False, server_default=u'')
    # Relationships
    roles = db.relationship('Role', secondary='users_roles',
                            backref=db.backref('users', lazy='dynamic'))

# OpenZeka: New table for usage tracking
# User usage table
class Usage(db.Model):
    __tablename__ = 'usage'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.id'))
    # usages = db.Column(db.Integer)
    usages = db.Column(db.String)
    user = db.relationship('User')

# Define the Role data model
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

# OpenZeka: New table Client
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
    # musteri turu ilerleyen donemde cesitlenecek
    client_type = db.Column(db.String(20), default='public')

    _redirect_uris = db.Column(db.Text)
    default_scope = db.Column(db.Text, default='api_access')

    user_id = db.Column(db.ForeignKey('users.id'))
    user = db.relationship('User')
    # token = db.relationship('Token')
    # db.ForeignKey('client.client_id', ondelete='CASCADE'),
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

# OpenZeka: New table Grant
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

# OpenZeka: New table Token
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



# Define the User registration form
# It augments the Flask-User RegisterForm with additional fields
class MyRegisterForm(RegisterForm):
    first_name = StringField('First name', validators=[
        validators.DataRequired('First name is required')])
    last_name = StringField('Last name', validators=[
        validators.DataRequired('Last name is required')])
    # OpenZeka:
    signup_terms = BooleanField('Signup Terms', validators=[
        validators.DataRequired('You should read and accept')])


# Define the User profile form
class UserProfileForm(Form):
    # OpenZeka: Profilepage show email adress
    email = StringField('Email Address')
    username = StringField('Username')
    first_name = StringField('First name', validators=[
        validators.DataRequired('First name is required')])
    last_name = StringField('Last name', validators=[
        validators.DataRequired('Last name is required')])
    submit = SubmitField('Save')


# OpenZeka:
class MyForm(Form):
   application_name = StringField('Application name', validators=[
       validators.DataRequired('Application name is required'), validators.Length(max=20)])
   submit = SubmitField('Create Application')

class ApplicationForm(Form):
   application_name = StringField('Application name', validators=[
        validators.DataRequired('Application name is required'), validators.Length(max=20)])
   client_id = StringField('Client id', validators=[
        validators.DataRequired('Client id is required')])
   client_secret = StringField('Client secret', validators=[
        validators.DataRequired('Client secret is required')])
   client_token = StringField();
   submit = SubmitField('Update Application')

# OpenZeka: Homepage image recognition demo form
class ImageDemoForm(Form):
    imagefile = FileField('Your photo')
    imageurl = StringField('Enter Image URL', validators=[
        validators.DataRequired('Image URL required')])
    submit = SubmitField('Tell me Image')

# OpenZeka:

class ImagenetClassifier(object):
    default_args = {
        'model_def_file': (
            '{}/../../models/bvlc_reference_caffenet/deploy.prototxt'.format(app.config['REPO_DIRNAME'])),
        'pretrained_model_file': (
            '{}/../../models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel'.format(app.config['REPO_DIRNAME'])),
        'mean_file': (
            '{}/../../python/caffe/imagenet/ilsvrc_2012_mean.npy'.format(app.config['REPO_DIRNAME'])),
        'class_labels_file': (
            '{}/../../data/ilsvrc12/synset_words.txt'.format(app.config['REPO_DIRNAME'])),
        'bet_file': (
            '{}/../../data/ilsvrc12/imagenet.bet.pickle'.format(app.config['REPO_DIRNAME'])),
    }
    for key, val in default_args.iteritems():
        if not os.path.exists(val):
            raise Exception(
                "File for {} is missing. Should be at: {}".format(key, val))
    default_args['image_dim'] = 256
    default_args['raw_scale'] = 255.

    def __init__(self, model_def_file, pretrained_model_file, mean_file,
                 raw_scale, class_labels_file, bet_file, image_dim, gpu_mode):
        logging.info('Loading net and associated files...')
        if gpu_mode:
            caffe.set_mode_gpu()
        else:
            caffe.set_mode_cpu()
        self.net = caffe.Classifier(
            model_def_file, pretrained_model_file,
            image_dims=(image_dim, image_dim), raw_scale=raw_scale,
            mean=np.load(mean_file).mean(1).mean(1), channel_swap=(2, 1, 0)
        )

        with open(class_labels_file) as f:
            labels_df = pd.DataFrame([
                {
                    'synset_id': l.strip().split(' ')[0],
                    'name': ' '.join(l.strip().split(' ')[1:]).split(',')[0]
                }
                for l in f.readlines()
            ])
        # self.labels = unicode(labels_df.sort('synset_id')['name'].values, "utf-8")
        self.labels = labels_df.sort('synset_id')['name'].values

        self.bet = cPickle.load(open(bet_file))
        # A bias to prefer children nodes in single-chain paths
        # I am setting the value to 0.1 as a quick, simple model.
        # We could use better psychological models here...
        self.bet['infogain'] -= np.array(self.bet['preferences']) * 0.1

    def classify_image(self, image):

        try:
            starttime = time.time()
            scores = self.net.predict([image], oversample=True).flatten()
            endtime = time.time()

            indices = (-scores).argsort()[:5]
            predictions = self.labels[indices]

            # In addition to the prediction text, we will also produce
            # the length for the progress bar visualization.
            meta = [
                (p, '%.5f' % scores[i])
                for i, p in zip(indices, predictions)
            ]
            logging.info('result: %s', str(meta))

            # Compute expected information gain
            expected_infogain = np.dot(
                self.bet['probmat'], scores[self.bet['idmapping']])
            expected_infogain *= self.bet['infogain']

            # sort the scores
            infogain_sort = expected_infogain.argsort()[::-1]
            bet_result = [(self.bet['words'][v], '%.5f' % expected_infogain[v])
                          for v in infogain_sort[:5]]
            logging.info('bet result: %s', str(bet_result))

            return (True, meta, bet_result, '%.3f' % (endtime - starttime))
        #
        except Exception as err:
            logging.info('Classification error: %s', err)
            return (False, 'Something went wrong when classifying the '
                           'image. Maybe try another one?')
class ImagenetClassifier_api(object):
    default_args = {
        'model_def_file': (
            '{}/../../models/bvlc_reference_caffenet/deploy.prototxt'.format(app.config['REPO_DIRNAME'])),
        'pretrained_model_file': (
            '{}/../../models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel'.format(app.config['REPO_DIRNAME'])),
        'mean_file': (
            '{}/../../python/caffe/imagenet/ilsvrc_2012_mean.npy'.format(app.config['REPO_DIRNAME'])),
        'class_labels_file': (
            '{}/../../data/ilsvrc12/synset_words.txt'.format(app.config['REPO_DIRNAME'])),
        'bet_file': (
            '{}/../../data/ilsvrc12/imagenet.bet.pickle'.format(app.config['REPO_DIRNAME'])),
    }
    for key, val in default_args.iteritems():
        if not os.path.exists(val):
            raise Exception(
                "File for {} is missing. Should be at: {}".format(key, val))
    default_args['image_dim'] = 256
    default_args['raw_scale'] = 255.

    def __init__(self, model_def_file, pretrained_model_file, mean_file,
                 raw_scale, class_labels_file, bet_file, image_dim, gpu_mode):
        logging.info('Loading net and associated files...')
        if gpu_mode:
            caffe.set_mode_gpu()
        else:
            caffe.set_mode_cpu()
        self.net = caffe.Classifier(
            model_def_file, pretrained_model_file,
            image_dims=(image_dim, image_dim), raw_scale=raw_scale,
            mean=np.load(mean_file).mean(1).mean(1), channel_swap=(2, 1, 0)
        )

        with open(class_labels_file) as f:
            labels_df = pd.DataFrame([
                {
                    'synset_id': l.strip().split(' ')[0],
                    'name': ' '.join(l.strip().split(' ')[1:]).split(',')[0]
                }
                for l in f.readlines()
            ])
        # self.labels = unicode(labels_df.sort('synset_id')['name'].values, "utf-8")
        self.labels = labels_df.sort('synset_id')['name'].values

        self.bet = cPickle.load(open(bet_file))
        # A bias to prefer children nodes in single-chain paths
        # I am setting the value to 0.1 as a quick, simple model.
        # We could use better psychological models here...
        self.bet['infogain'] -= np.array(self.bet['preferences']) * 0.1

    def classify_image(self, image):

        try:
            starttime = time.time()
            scores = self.net.predict([image], oversample=True).flatten()
            endtime = time.time()

            indices = (-scores).argsort()[:5]
            predictions = self.labels[indices]

            # In addition to the prediction text, we will also produce
            # the length for the progress bar visualization.
            meta = [
                (p, '%.5f' % scores[i])
                for i, p in zip(indices, predictions)
            ]
            logging.info('result: %s', str(meta))

            # Compute expected information gain
            expected_infogain = np.dot(
                self.bet['probmat'], scores[self.bet['idmapping']])
            expected_infogain *= self.bet['infogain']

            # sort the scores
            infogain_sort = expected_infogain.argsort()[::-1]
            bet_result = [(self.bet['words'][v], '%.5f' % expected_infogain[v])
                          for v in infogain_sort[:5]]
            logging.info('bet result: %s', str(bet_result))
            # meta = unicode(meta, "utf8")
            # meta = meta.decode("utf-8")
            # image_={'image',image}
            # return (True, meta, bet_result, '%.3f' % (endtime - starttime))
            # confidence olarak kullanılan olasılık yani c değeri float tipini çevrilip 100 ile çarpılıyor. Bu sayede yüzde olarak sonuc donduruluyor
            new = []
            for t, c in meta:
                new.append({"tag": t, "probability": float(c)*100})

            python_object = {'tags': new,
                             'time': '%.3f' % (endtime - starttime)}
            return (python_object)
        #
        except Exception as err:
            logging.info('Classification error: %s', err)
            return (False, 'Something went wrong when classifying the '
                           'image. Maybe try another one?')

