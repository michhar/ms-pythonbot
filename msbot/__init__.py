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

# cwd = os.getcwd()
# auth_config = os.path.join(cwd, 'auth_config.json')
auth_config = 'https://gist.githubusercontent.com/michhar/d51d5fa5d4a3ec8f9b73e9d47db906b4/raw/bbcafd3cd4b8da4bed19ceb0b8511cbc7da8e1bb/auth_config.json'

config = {'OIDC_CLIENT_SECRETS': auth_config,
'OIDC_SCOPES': ["https://api.botframework.com/.default"],
'OIDC_RESOURCE_SERVER_ONLY': True}

app.config.update(config)
oidc = OpenIDConnect(app)

import msbot.views
