
"""
This script runs the FlaskWebProject1 application using a development server.
"""

from os import environ
from msbot import app

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '3978'))
    except ValueError:
        PORT = 3978
    app.run(HOST, PORT)
