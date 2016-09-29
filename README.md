# OpenZeka Image Recognition Web and API Server

OpenZeka is written python with using [Flask-User](pythonhosted.org/Flask-User) as a skeleton and [Caffe](caffe.berkeleyvision.org) as a Recognition Engine.
OpenZeka has two part Web Server and API Server.

## OpenZeka Web Server
Users can create and manage their account. Also users can create applications and track usages. Every application has unique Client Id and Client Secret. With using web server user can generate tokens.

## OpenZeka API Server
API use [OAuth2 Server](flask-oauthlib.readthedocs.io/en/latest/oauth2.html) for authorization. User can generate token with using `Client Id` and `Client Secret`. With using token users can make image recognition requests.
Tokens have a lifetime. You can change token lifetime **app/startup/openzeka_common_settings.py**
You can see [OpenZeka API Requests](https://github.com/ferhatkurt/openzeka/wiki/API-Requests).

# Installing OpenZeka
OpenZeka tested with Ubuntu 14.04, Ubuntu 16.04, Jetson TX1, and Jetson TK1. Not tested with Windows and MacOS. We highly recommend you to share install experiment with us. OpenZeka basicly can run any operating system if you install Caffe and pycaffe.
We prepared easy install script. You can click and follow instructions.
 1. [Installing OpenZeka for Ubuntu 14.04](https://github.com/ferhatkurt/openzeka/wiki/Installing-OpenZeka-for-Ubuntu-14.04)
 2. [Installing OpenZeka for Ubuntu 16.04](https://github.com/ferhatkurt/openzeka/wiki/Installing-OpenZeka-for-Ubuntu-16.04)
 3. [Installing OpenZeka for Jetson TX1](https://github.com/ferhatkurt/openzeka/wiki/Installing-OpenZeka-for-Jetson-TX1)
 4. [Installing OpenZeka for Jetson TK1](https://github.com/ferhatkurt/openzeka/wiki/Installing-OpenZeka-for-Jetson-TK1)

If you want to use virtual enviroment install [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html) then install OpenZeka.

# Configuration of OpenZeka

Before we can use this application, we will have to configure the database URL and SMTP account
that will be used to access the database and to send emails. Defau

Settings common to all environments are found in `app/startup/common_settings.py`

The example environment-specific settings are found in `app/openzeka_env_settings_example.py`

Copy the `app/openzeka_env_settings_example.py` to an `openzeka_env_settings.py` that resides **outside** the code directory and point the OS environment variable `OPENZEKA_ENV_SETTINGS_FILE` to this file.

For convenience, you can set OPENZEKA_ENV_SETTINGS_FILE in your `~/.bashrc` or `~/.bash_profile` shell configuration file.

    echo "export OPENZEKA_ENV_SETTINGS_FILE=/path/to/openzeka_env_settings.py " >> ~/.bashrc

Now edit the `/path/to/openzeka_env_settings.py` file. You can find details in the file. In order to run email service you need **enter your email server details**. Also don't forget to change **info@localhost** to your email. Unhandled exceptions will now send an email message to ADMINS.

    ADMINS = [
        '"Open Zeka Admin" <info@localhost>',
        ]

### First-time Running OpenZeka
First-time running will create OpenZeka database with 2 users. You can use this users details with your website.

 - email `user@example.com` with password `Password1`.
 - email `admin@example.com` with password `Password1`.

**You can also try to install OpenZeka with [virtualenvwrapper](github.com/ferhatkurt/openzeka/wiki/Virtualenvwrapper-for-OpenZeka)**

## Developer benefits
* Tested on Python 2.7, 3.3, and 3.4
* Well organized directories with lots of comments
  * app/models
  * app/startup
  * app/views
* HTML5 BoilerPlate / jQuery / Bootstrap layout template
* Few dependencies (Flask-SQLAlchemy, Flask-WTF, Flask-User, Flask-Migrate)
* Includes Flask-User user management
  * Register, Confirm email, Login, Logout
  * Change username/email/password, Forgot password
* SMTPHandler for error-level log messages -- sends emails on unhandled exceptions
* Includes `py.test` test framework
* Includes `alembic` database migration framework

## Acknowledgements
* [Caffe](http://caffe.berkeleyvision.org)

With thanks to the following Flask extensions:
* [Flask-User](http://pythonhosted.org/Flask-User/)
* [Flask-User-starter-app](https://github.com/lingthio/Flask-User-starter-app)
* [Flask-OAuthlib](https://github.com/lepture/flask-oauthlib)
* [Alembic](http://alembic.zzzcomputing.com/en/latest/)
* [Flask-Migrate](http://flask-migrate.readthedocs.io/en/latest/)
