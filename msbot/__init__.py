"""
The flask application package.
"""

#####################################################################
# Create the Flask app
#####################################################################


from flask import Flask
app = Flask(__name__)

import msbot.views

app.config['DEBUG'] = True
