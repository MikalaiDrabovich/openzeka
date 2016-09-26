"""
Open Zeka Image Recognition Web & API Server
This is pre release version
http://openzeka.com
http://github.com/ferhatkurt/openzeka

Based on Flask-user starter app

Open Zeka v.0.0.1pre
v.X.Y.Z (MAJOR.MINOR.PATCH)
Version control, Semantic Versioning - http://semver.org/

common_settings.py is a common settings page
In order to call configuration variables in Jinja template use config['MY_CONFIGURATION'] or config.MY_CONFIGURATION.
"""
import os

OPENZEKA_VERSION = "v.0.0.1"

# REPO_DIRNAME will use to find models directory
# Open Zeka will use openzeka/models/bvlc_reference_caffenet
# If you want you can change it your cafe main directory
REPO_DIRNAME = os.path.dirname(os.path.realpath(__file__))
# Token Lifetime
OAUTH2_PROVIDER_TOKEN_EXPIRES_IN = 259200 #72 hours:259200, 24 hours:86400
# Open Zeka image upload directory, default is openzeka/uploads
UPLOAD_FOLDER = os.path.dirname(os.path.realpath(__file__)) + '/../../uploads'
# Allowed image type for recognition process
ALLOWED_IMAGE_EXTENSIONS = set(['png', 'bmp', 'jpg', 'jpe', 'jpeg', 'gif'])
# Set True if you want to API debug mode
API_DEBUD = False


# ***********************************
# Settings common to all environments
# ***********************************

# Application settings
APP_NAME = "Open Zeka"
APP_SYSTEM_ERROR_SUBJECT_LINE = APP_NAME + " system error"

# Flask settings
CSRF_ENABLED = True

# Flask-User settings
USER_APP_NAME = APP_NAME
USER_ENABLE_CHANGE_PASSWORD = True  # Allow users to change their password
USER_ENABLE_CHANGE_USERNAME = False  # Allow users to change their username
USER_ENABLE_CONFIRM_EMAIL = True  # Force users to confirm their email
USER_ENABLE_FORGOT_PASSWORD = True  # Allow users to reset their passwords
USER_ENABLE_EMAIL = True  # Register with Email
USER_ENABLE_REGISTRATION = True  # Allow new users to register
USER_ENABLE_RETYPE_PASSWORD = True  # Prompt for `retype password` in:
USER_ENABLE_USERNAME = True  # Register and Login with username
USER_AFTER_LOGIN_ENDPOINT = 'core.user_page'
USER_AFTER_LOGOUT_ENDPOINT = 'core.home_page'

# OpenZeka: Redirect page to change password after changind password
# https://pythonhosted.org/Flask-User/api.html
USER_AFTER_CHANGE_PASSWORD_ENDPOINT = 'user.change_password'
