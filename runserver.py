"""
This script runs the FlaskAppAML application using a development server.
"""

import os
from msbot import app

#####################################################################
# Run main app - Windows OS only!
#####################################################################

if __name__ == '__main__':
    # Start redis server as broker for celery processes first
    os.system('start /B redis\\redis-server.exe redis\\redis.windows.conf')

    # Start celery for asynchronous task queues
    os.system('start /B celery -A server_flask.celery_app worker -l info')

    # Run flask app on port specified here
    app.run(host='127.0.0.1', port=3978, debug=True)