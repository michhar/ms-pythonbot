"""
This script runs the ms-pythonbot application
=======
This script runs the msbot application using a development server.

To test:
  - Download either redis for unix and build (https://redis.io/download)
    or redis for windows (https://github.com/ServiceStack/redis-windows)
  - Ensure redis server app is in PATH and if there's a conf file
    required ensure it is accessible either here or in a given path (Windows).
  - Ensure celery and all packages from the requirements.txt file
      are installed locally or if using a virtual environment inside
      that environment (check Lib -> site-packages)
  - See REAMDE for more information on running this example

"""

from msbot import app

#####################################################################
# Run main app - Cross-platform compatibility
#####################################################################

if __name__ == '__main__':
    # Run flask app on port specified here
    app.run(host='localhost', port=3978, debug=True)
