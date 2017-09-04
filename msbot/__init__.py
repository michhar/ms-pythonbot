"""
The flask application package.
"""

#####################################################################
# Create the Flask app
#####################################################################


from flask import Flask
from flask_oidc import OpenIDConnect
from .callback_utils import Callbacks
import os
import json


app = Flask(__name__)
app.config['DEBUG'] = True

cwd = os.getcwd()
auth_config_tmpl = os.path.join(cwd, 'msbot', 'auth_config_template.json')
auth_config = os.path.join('..', cwd, 'auth_config.json')

# For unix compatibility
auth_config = os.path.join(cwd, 'auth_config.json')


with open(auth_config_tmpl, 'r') as data_file:
    data = json.load(data_file)
    data['web']['client_id'] = os.getenv('MICROSOFT_CLIENT_ID', 'foo')
    data['web']['client_secret'] = os.getenv('MICROSOFT_CLIENT_SECRET', 'bar')
    print(data)
    with open(auth_config, 'w') as auth:
        json.dump(data, auth)


config = {'OIDC_CLIENT_SECRETS': auth_config,
          'OIDC_SCOPES': ["https://api.botframework.com/.default"],
          'OIDC_RESOURCE_SERVER_ONLY': True}

app.config.update(config)
oidc = OpenIDConnect(app)

app_backend = Callbacks()

import msbot.views
