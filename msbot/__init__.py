"""
The flask application package.
"""

#####################################################################
# Create the Flask app
#####################################################################


from flask import Flask
from flask_oidc import OpenIDConnect
import os
import urllib.request

app = Flask(__name__)

app.config['DEBUG'] = True

cwd = os.getcwd()
# auth_config = os.path.join(cwd, 'auth_config.json')
url = 'https://gist.githubusercontent.com/michhar/d51d5fa5d4a3ec8f9b73e9d47db906b4/raw/2faf799dda51087ff75ebe861933b305b42501f6/auth_config.json'
file_name = os.path.join(cwd, 'msbot', 'auth_config.json')
# Download the file from `url` and save it locally under `file_name`:
with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
    data = response.read() # a `bytes` object
    out_file.write(data)

auth_config = file_name
config = {'OIDC_CLIENT_SECRETS': auth_config,
'OIDC_SCOPES': ["https://api.botframework.com/.default"],
'OIDC_RESOURCE_SERVER_ONLY': True}

app.config.update(config)
oidc = OpenIDConnect(app)

import msbot.views
