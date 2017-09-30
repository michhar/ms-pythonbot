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
          'SERVER_NAME': os.getenv('SERVER_NAME', 'localhost'),
          'SECRET_KEY': 'dev',
          'PREFERRED_URL_SCHEME': 'https',
          'DEBUG': True
         }

app.config.update(config)

client_info = {
            'client_id': os.getenv('MICROSOFT_CLIENT_ID', 'foo'),
            'client_secret': os.getenv('MICROSOFT_CLIENT_SECRET', 'bar'),
            # 'scope': 'https://api.botframework.com/.default'

}

provider_config = {
            'issuer': 'https://api.botframework.com',
            'authorization_endpoint': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
            'token_endpoint': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
            'userinfo_endpoint': 'https://login.microsoftonline.com/common/oauth2/v2.0/userinfo',
            # 'grant_type': 'client_credentials',
            # 'scope': 'https://api.botframework.com/.default'
}

auth = OIDCAuthentication(app,
                          provider_configuration_info=provider_config,
                          client_registration_info=client_info)

app_backend = Callbacks()

import msbot.views
