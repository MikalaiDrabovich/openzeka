# coding: utf-8
"""
Open Zeka Image Recognition Web & API Server
This is pre release version
http://openzeka.com
http://github.com/ferhatkurt/openzeka

Based on Flask-user starter app
"""


from flask import redirect, render_template, render_template_string, Blueprint
# OpenZeka: added jsonify
from flask import request, url_for, jsonify
from flask_user import current_user, login_required, roles_accepted
from app import app, db
# OpenZeka: added MyForm, ApplicationForm, ImageDemoForm, Client, Token, Usage
from app.core.models import UserProfileForm, MyForm, ApplicationForm, ImageDemoForm, Client, Token, Usage

# OpenZeka
from flask_user.signals import user_registered, user_confirmed_email
from datetime import datetime
import calendar
import requests, json
from werkzeug.security import gen_salt
# Caffe
import urllib
import cStringIO as StringIO
import logging
import caffe
import os
import werkzeug

core_blueprint = Blueprint('core', __name__, url_prefix='/')

# OpenZeka: New user registration save user ip address
@user_registered.connect_via(app)
def _track_registrations(sender, user, **extra):
    user.reg_ip = request.remote_addr
    db.session.add(user)
    db.session.commit()

# OpenZeka: After user email confirmation s processes will be done
@user_confirmed_email.connect_via(app)
def _track_confirmation(sender, user, **extra):
    i = datetime.now()
    usage_date = "%s,%s,%s" % (i.day, i.month, i.year)
    today = datetime.now()
    next_month = add_months(today, 1)
    item = Usage(
        user_id=user.id,
        # Adding 25000 limit. Limit information should be declare while registering
        usages=usage_date+","+str(next_month[0])+','+str(next_month[1])+','+str(next_month[2])+",0,25000"
    )
    db.session.add(item)
    db.session.commit()


# The Home page is accessible to anyone
@core_blueprint.route('')
def home_page():
    form=ImageDemoForm()
    return render_template('core/home_page.html', form=form)


# The User page is accessible to authenticated users (users that have logged in)
@core_blueprint.route('user')
@login_required  # Limits access to authenticated users
def user_page():
    return render_template('core/user_page.html')


# The Admin page is accessible to users with the 'admin' role
@core_blueprint.route('admin')
@roles_accepted('admin')  # Limits access to users with the 'admin' role
def admin_page():
    return render_template('core/admin_page.html')


@core_blueprint.route('user/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    # Initialize form
    form = UserProfileForm(request.form, current_user)

    # Process valid POST
    if request.method == 'POST' and form.validate():
        # Copy form fields to user_profile fields
        form.populate_obj(current_user)
        # Save user_profile
        db.session.commit()
        # Redirect to home page
        #return redirect(url_for('core.home_page'))
        # OpenZeka: After updating user will turn form page
        return redirect(url_for('core.user_profile_page'))

    # Process GET or invalid POST
    return render_template('core/user_profile_page.html',
                           form=form)

# Create client id and secret key
@core_blueprint.route('application/create', methods=['GET', 'POST'])
@login_required  # Limits access to authenticated users
def create_application():
    # Initialize form
    form = MyForm(request.form, current_user)
    user = current_user
    # Firsttime calling create_application
    if not (request.method == 'POST' and form.validate()):
        application_num = Client.query.filter_by(user_id=user.id).count()
        return render_template('application/create_application.html', form=form, application_number=application_num)
    # After entering application name and validation details adding to database
    item = Client(
        client_id=gen_salt(32),
        client_secret=gen_salt(32),
        application_name=request.form.get('application_name'),
        default_scope='api_access',
        _redirect_uris='https://api.openzeka.com/authorized ',
        user_id=user.id,
    )
    db.session.add(item)
    db.session.commit()
    form_application = ApplicationForm(request.form, item)
    return render_template('application/manage_application_page.html', application=item, form=form_application)

# Application edit id
@core_blueprint.route('application/edit/<id>', methods=['GET', 'POST'])
@login_required  # Limits access to authenticated users
def application_edit(id):
    application = Client.query.filter_by(application_id=id).first_or_404()
    form = ApplicationForm(request.form, application)
    # Firsttime calling create_application
    if request.method == 'POST' and form.validate():
        application.application_name = request.form.get('application_name')
        db.session.add(application)
        db.session.commit()
        active = application.application_id
        # user = current_user
        applications = Client.query.filter_by(user_id=application.user_id).all()
        number = Client.query.filter_by(user_id=application.user_id).count()
        return render_template('application/list_applications.html', applications=applications, number=number, active=active)

    return render_template('application/manage_application_page.html', application=application, form=form)

# Application delete id
@core_blueprint.route('application/delete/<id>', methods=['GET', 'POST'])
@login_required  # Limits access to authenticated users
def application_delete(id):
    client = Client.query.filter_by(application_id=id).first()
    token = Token.query.filter_by(client_id=client.client_id).first()
    if token:
        db.session.delete(token)
    db.session.delete(client)
    db.session.commit()

    return list_application()

# Create client id and secret key
@core_blueprint.route('application/list', methods=['GET', 'POST'])
@login_required  # Limits access to authenticated users
def list_application():
    user = current_user
    applications = Client.query.filter_by(user_id=user.id).all()
    app_first = Client.query.filter_by(user_id=user.id).first()
    form = ApplicationForm(request.form, app_first)
    number = Client.query.filter_by(user_id=user.id).count()
    # ilk applicasyonu secmek icin sorgu yapip active degerine id isini atadik
    active = 0
    if number > 0:
        active = app_first.application_id
    return render_template('application/list_applications.html', applications=applications, number=number, active=active, form=form)

@core_blueprint.route('save_token')
def save_token():
    client_id=request.args.get('client_id')
    client_secret=request.args.get('client_secret')
    grant_type='client_credentials'
    # result = request.post('http://localhost:9000/oauth/token', client_id)
    # data = 'client_id='+client_id+'&client_secret=HS6gm7JoGBFH41oWB2KSz85JqcDb5hoMiWDGQFZMWLRvdOtp3V&grant_type=client_credentials'

    # result = requests.post('http://localhost:9000/oauth/token', data=data)
    # result = requests.get('http://localhost:9000/oauth/token?client_id=0wd8Js7PoHy71me9wZ9kaPk1a1CtnkOPKMIq85iV&client_secret=i54wCpJSXOph2h0dKVaXAKcrBmaSHXdC1nWKh1BBWOGh2ng4D6&grant_type=client_credentials')
    result = requests.post('http://localhost:9000/oauth/token', data = {'client_id': client_id, 'client_secret': client_secret, 'grant_type': 'client_credentials'})
    json_data = json.loads(result.text)
    return jsonify(result=json_data['access_token'])
    # return jsonify(result=json_data)

# Usage sayfasi
@core_blueprint.route('usage')
@login_required  # Limits access to authenticated users
def usage_report():
    user = current_user
    usage_ = Usage.query.filter_by(user_id=user.id).first()
    # usages format: start day,month,year,end day,month,year,usage,limit;start day,month,year,end day,month,year,usage,limit;
    # sample: 15,7,2016,15,8,2016,15300,25000;15,8,2016,15,09,2016,20000,25000;15,9,2016,15,10,2016,1,25000
    if ';' in usage_.usages:
        months_with_usage = usage_.usages.split(";")
        # select latest month
        last_month_with_usage = months_with_usage.pop()
        last_month_with_usage = last_month_with_usage.split(",")
        has_old_month = True
        old_months_with_usage = reversed(months_with_usage)
    else:
        has_old_month = False
        old_months_with_usage = False
        last_month_with_usage = usage_.usages.split(",")
    today = datetime.now()
    past_month = last_month_with_usage
    past = datetime(int(past_month[5]), int(past_month[4]), int(past_month[3]))
    if (today > past):
        start_date = "%s,%s,%s" % (today.day, today.month, today.year)
        # start_date = datetime(int(latest_usage[2]), int(latest_usage[1]), int(latest_usage[0]))
        next_month = add_months(today, 1)
        # next_month = "1,9,2016"
        usage_.usages = usage_.usages + ";" + start_date + "," + str(next_month[0]) + ',' + str(
            next_month[1]) + ',' + str(next_month[2]) + ",0,25000"
        db.session.add(usage_)
        db.session.commit()
        # Normally this method should write again but we will recall samepage again.
        return redirect(url_for('core.usage_report'))
    return render_template('application/usage.html', has_old_month=has_old_month, old_months_with_usage=old_months_with_usage, latest_month=last_month_with_usage, progres_bar=progres_bar)

# Usage sayfasi
@core_blueprint.route('billing')
@login_required  # Limits access to authenticated users
def billing_page():
    # user = current_user
    # usage_ = Usage.query.filter_by(user_id=user.id).first()
    # user_limit=1000
    # usage_status = (usage_.usages/user_limit)*100

    # return render_template('core/billing.html', usage=usage_.usages, usage_status=usage_status)
    return render_template('application/billing.html')

# OpenZeka: Homepage demo form
@core_blueprint.route('classify_url', methods=['GET'])
def classify_url():
    # Dogrulama icin asagidaki gibi bir form cagiracagiz
    # form = ImageDemoForm(request.form)
    form = ImageDemoForm(request.form)
    imageurl = request.args.get('imageurl', '')
    # if not(form.validate()):
    #     return render_template(/classify_upload
    #         'core/home_page.html', form=form
    #     )
    # if not (form.validate_on_submit()):
    #     return render_template(
    #             'core/home_page.html', form=form
    #     )
    try:
        string_buffer = StringIO.StringIO(
            urllib.urlopen(imageurl).read())
        image = caffe.io.load_image(string_buffer)

    except Exception as err:
        # For any exception we encounter in reading the image, we will just
        # not continue.
        logging.info('URL Image open error: %s', err)
        return render_template(
            'core/home_page.html', has_result=True,
            result=(False, 'Cannot open image from URL.'), imagesrc=imageurl, form=form
            )

    logging.info('Image: %s', imageurl)
    result = app.clf.classify_image(image)
    return render_template(
        'core/home_page.html', has_result=True, result=result, imagesrc=imageurl, imageurl=imageurl, form=form, progres_bar=progres_bar)

@core_blueprint.route('classify_upload', methods=['POST'])
def classify_upload():
    form = ImageDemoForm()
    try:
        # We will save the file to disk for possible data collection.
        imagefile = request.files['imagefile']
        # filename_ = str(datetime.datetime.now()).replace(' ', '_') + \
        filename_ = str(datetime.now()).replace(' ', '_') + \
                    werkzeug.secure_filename(imagefile.filename)
        filename = os.path.join(app.config['UPLOAD_FOLDER'], filename_)
        imagefile.save(filename)
        logging.info('Saving to %s.', filename)
        image = open_oriented_im(filename)

    except Exception as err:
        logging.info('Uploaded image open error: %s', err)
        return render_template(
            'core/home_page.html', has_result=True,
            result=(False, 'Cannot open uploaded image.'), form=form
        )

    result = app.clf.classify_image(image)
    # result = unicode(result, "utf8")
    return render_template(
        'core/home_page.html', has_result=True, result=result,
        imagesrc=embed_image_html(image), form=form, progres_bar=progres_bar
    )
# Register blueprint
app.register_blueprint(core_blueprint)

# OpenZeka: Homepage image box
def embed_image_html(image):
    """Creates an image embedded in HTML base64 format."""
    image_pil = Image.fromarray((255 * image).astype('uint8'))
    image_pil = image_pil.resize((256, 256))
    string_buf = StringIO.StringIO()
    image_pil.save(string_buf, format='png')
    data = string_buf.getvalue().encode('base64').replace('\n', '')
    return 'data:image/png;base64,' + data

# OpenZeka: Adding month to usage
# http://stackoverflow.com/questions/4130922/how-to-increment-datetime-by-custom-months-in-python-without-using-library
def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12)
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return (day,month,year)

# OpenZeka: Caffe web demo exifutil.py content
"""
This script handles the skimage exif problem.
"""

from PIL import Image
import numpy as np

ORIENTATIONS = {   # used in apply_orientation
    2: (Image.FLIP_LEFT_RIGHT,),
    3: (Image.ROTATE_180,),
    4: (Image.FLIP_TOP_BOTTOM,),
    5: (Image.FLIP_LEFT_RIGHT, Image.ROTATE_90),
    6: (Image.ROTATE_270,),
    7: (Image.FLIP_LEFT_RIGHT, Image.ROTATE_270),
    8: (Image.ROTATE_90,)
}


def open_oriented_im(im_path):
    im = Image.open(im_path)
    if hasattr(im, '_getexif'):
        exif = im._getexif()
        if exif is not None and 274 in exif:
            orientation = exif[274]
            im = apply_orientation(im, orientation)
    img = np.asarray(im).astype(np.float32) / 255.
    if img.ndim == 2:
        img = img[:, :, np.newaxis]
        img = np.tile(img, (1, 1, 3))
    elif img.shape[2] == 4:
        img = img[:, :, :3]
    return img


def apply_orientation(im, orientation):
    if orientation in ORIENTATIONS:
        for method in ORIENTATIONS[orientation]:
            im = im.transpose(method)
    return im
progres_bar = ['-success', '-info', '', '-warning', '-danger']