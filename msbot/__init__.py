"""
The flask application package.
"""

#####################################################################
# Create the Flask app
#####################################################################


from flask import Flask
from .callback_utils import Callbacks
import os
from flask_pyoidc.flask_pyoidc import OIDCAuthentication


app = Flask(__name__)

### Flask-pyoidc ###

config = {
          'SERVER_NAME': 'localhost:3978',
          'SECRET_KEY': 'dev',
          'DEBUG': True
         }
app.config.update(config)

client_info = {
            'client_id': os.getenv('MICROSOFT_CLIENT_ID', 'foo'),
            'client_secret': os.getenv('MICROSOFT_CLIENT_SECRET', 'bar'),

}

provider_config = {
            'issuer': 'https://login.microsoftonline.com',
            'authorization_endpoint': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
            'token_endpoint': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
            'userinfo_endpoint': 'https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token',
            'grant_type': 'client_credentials',
            'scope': 'https://api.botframework.com/.default'
}

auth = OIDCAuthentication(app,
                          provider_configuration_info=provider_config,
                          client_registration_info=client_info)

app_backend = Callbacks()

import msbot.views
