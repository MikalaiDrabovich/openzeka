# This file starts the WSGI web application.
# - Heroku starts gunicorn, which loads Procfile, which starts manage.py
#OpenZeka:
from app.core.models import ImagenetClassifier
import optparse
import os
import logging

from app import create_app


app = create_app()
# app.config.update(dict(
#     DATABASE=os.path.join(app.root_path, 'flaskr.db'),
#     SECRET_KEY='development key',
#     USERNAME='admin',
#     PASSWORD='default'
# ))

# Start a development web server if executed from the command line
if __name__ == "__main__":
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
        type='int', default=5000)
    parser.add_option(
        '-g', '--gpu',
        help="use gpu mode",
        action='store_true', default=False)

    opts, args = parser.parse_args()
    ImagenetClassifier.default_args.update({'gpu_mode': opts.gpu})

    # Initialize classifier + warm start by forward for allocation
    app.clf = ImagenetClassifier(**ImagenetClassifier.default_args)
    app.clf.net.forward()
    logging.getLogger().setLevel(logging.DEBUG)
    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    if opts.debug:
        app.run(debug=True, host='0.0.0.0', port=opts.port)
    else:
        app.run(host='0.0.0.0', port=opts.port)
