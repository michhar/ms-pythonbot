## MS-Pythonbot tl;dr

A first stab at a Microsoft Bot Framework Python bot using the REST API.  See below on how it works and how to run it locally with the Emulator.

## How it works

[Redis](https://redis.io/) is used here as an in-memory data structure store and message broker.

[Celery](http://www.celeryproject.org/) is used for asynchronous task queues and scheduling in combination with flask.

[Flask](http://flask.pocoo.org/) is the web app framework used here for message routing and where all of the bot logic is written.

[Flask-OpenID](https://github.com/puiterwijk/flask-oidc) is used for authentication (decorates the routing function in the bot app - see code).

## How to run

This example is a "Hi there!" and news fetching Python bot using the [Flask microframework](http://flask.pocoo.org/) to work with the Bot Framework on Azure or even just locally with the Bot Framework Emulator (recommended to use for testing and dev).

#### Setup

NOTE:  The flask app tests to see which OS the app is on and decides how to call the necessary dependencies.

* Download the Bot Framework Emulator for local testing (https://github.com/Microsoft/BotFramework-Emulator#download) - multiple OS compatibility.

##### Unix

1. Download redis for unix and build (https://redis.io/download)
2. Change the name of the redis folder to 'redisunix' under `ms-pythonbot` root folder so that the app can find it (thus it will have `redis-server` in the path `redisunix/src`).

##### Windows

 1. Download and set up redis for windows (https://github.com/ServiceStack/redis-windows)
 2. Change the name of the windows redis to 'rediswin' (thus it will have `redis-server.exe` in the path `rediswin\`).

#### Check

Ensure Celery and all packages from the requirements.txt file are installed locally or if using a virtual environment inside that environment (check Lib -> site-packages just to be sure).

#### Run

From the `ms-pythonbot` base folder:

    python runserver.py

This will start the Redis server as a message broker and the Celery program as a task queue.

#### Test locally in emulator

1. Open up the BF Emulator (usually called `botframework-emulator` on your system)
1. Click on the "Enter your endpoint URL" and select or type in `http://localhost:3978/api/messages`
2. Leave the "Microsoft App ID" and "Microsoft App Password" blank unless you have these and have ngrok set up
3. Click "CONNECT"

You should see in the Log window a "conversationUpdate" appear twice with no errors.  If there's an error ensure you have the `runserver.py` script going.

## TODO

1.  Keep the messages from a bot to one worker on celery
1.  Deploy to Azure
2.  Generalize Flask integration for future bots
3.  Explore other options than Celery for task queues (asyncio or Redis Queue)

## Future directions

Feed back into and leverage a python botframework wrapper.
