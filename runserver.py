"""
This script runs the ms-pythonbot application
=======
This script runs the msbot application using a development server.

To test:
  - Download either redis for unix and build (https://redis.io/download)
    or redis for windows (https://github.com/ServiceStack/redis-windows)
  - If on unix, place the redis folder in a folder called 'redisunix' and
      if on Windows place the windows redis in a folder 'rediswin' -> this
      script tests the os platform to decide which folder to use
  - Ensure celery and all packages from the requirements.txt file
      are installed locally or if using a virtual environment inside
      that environment (check Lib -> site-packages)
  - See REAMDE for more information

"""

import os
from msbot import app

from sys import platform as _platform

#####################################################################
# Run main app - Cross-platform compatibility
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
