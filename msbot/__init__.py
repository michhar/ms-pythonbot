"""
The flask application package.
"""

#####################################################################
# Create the Flask app
#####################################################################


from flask import Flask
from flask_oidc import OpenIDConnect
import os

app = Flask(__name__)


app.config['DEBUG'] = True

cwd = os.getcwd()
auth_config = os.path.join(cwd, 'auth_config.json')

config = {'OIDC_CLIENT_SECRETS': auth_config,
'OIDC_SCOPES': ["https://api.botframework.com/.default"],
'OIDC_RESOURCE_SERVER_ONLY': True}

app.config.update(config)
oidc = OpenIDConnect(app)

import msbot.views