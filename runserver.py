"""
This script runs the FlaskAppAML application using a development server.
"""

import os
from msbot import app

from sys import platform as _platform

#####################################################################
# Run main app - Windows OS only!
#####################################################################

if __name__ == '__main__':

    # Test system platform to decide which way to start celery and redis

    # Win
    if _platform.startswith("win"):
        # Start redis server as broker for celery processes first
        os.system('start /B rediswin\\redis-server.exe rediswin\\redis.windows.conf')
        # Start celery for asynchronous task queues
        os.system('start /B celery -A msbot.views.celery_app worker -l info')
    # Linus or Mac OSX
    else: #_platform.startswith("darwin") or _platform.startswith("linux" ):
        # Start redis server as broker for celery processes first
        os.system('redisunix/src/redis-server &')
        # Start celery for asynchronous task queues
        os.system('celery -A msbot.views.celery_app worker -l info &')


    # Run flask app on port specified here
    app.run(host='localhost', port=3978, debug=True)