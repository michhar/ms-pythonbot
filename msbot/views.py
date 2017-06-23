"""
Flask app for testing the OpenID Connect extension.
"""
from flask import Flask, jsonify, request, render_template, Response, g
from flask_oidc import OpenIDConnect

import http.client
import urllib.request
import urllib.parse
import urllib.error
import json
import datetime
import re
import os
import requests

# from celery import Celery
from msbot import app, oidc, app_backend
from .callback_utils import Output, Input


#####################################################################
# Add celery support for asynchronous calls
# (note: must also run celery worker and redis server for this example
#   to work - see README/docs)
#####################################################################

# Method for integrating celery with Flask for task queueing

# # Our main app page/route
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     """Renders the home page which is the CNS of the web app currently,
#     nothing pretty."""
#     return render_template('index.html', title='pythonbot')


# def make_celery(myapp):
#     celery = Celery('views', backend=myapp.config['CELERY_RESULT_BACKEND'],
#                     broker=myapp.config['CELERY_BROKER_URL'])
#     celery.conf.update(myapp.config)
#     TaskBase = celery.Task

#     class ContextTask(TaskBase):
#         abstract = True

#         def __call__(self, *args, **kwargs):
#             with myapp.app_context():
#                 return TaskBase.__call__(self, *args, **kwargs)
#     celery.Task = ContextTask
#     return celery


# app.config.update(
#     CELERY_BROKER_URL='redis://localhost:6379',
#     CELERY_RESULT_BACKEND='redis://localhost:6379'
# )
# celery_app = make_celery(app)

#####################################################################
# Main route for messaging
#####################################################################

@app.route('/')
@oidc.accept_token()
def index():
    return jsonify({'message':'too many secrets'}), 200, {
        'Content-Type': 'application/json'
    }

@app.route('/api/messages', methods=['POST', 'GET'])
@app_backend.callback(Output('id', 'value'))
@oidc.accept_token()
def messages():
    if request.method == "POST":
        # User message to bot
        data = request.json

        # Async methods run as tasks with celery backend
        if data["type"] == "conversationUpdate":
            # Add the members to the conversation
            initiateChat.delay(data)
        else:
            # The bot responds to the user
            respondToClient.delay(data)

        # return Response(
        #     mimetype='application/json',
        #     status=202
        # )

    return jsonify({'message': "Invalid request method"}), 405, {
        'Content-Type': 'application/json'
    }


#####################################################################
# Create the respond function to send message back to user
#####################################################################

def respond(serviceUrl, channelId, replyToId, fromData,
            recipientData, message, messageType, conversation):
    responseURL = serviceUrl + \
        "/v3/conversations/{}/activities/{}".format(conversation["id"],
                                                    replyToId)

    requests.post(
        url=responseURL,
        json={
            "type": messageType,
            "text": message,
            "locale": "en-US",
            "from": fromData,
            "timestamp": datetime.datetime.now()
            .strftime("%Y-%m-%dT%H:%M:%S.%f%zZ"),
            "localTimestamp": datetime.datetime.now()
            .strftime("%Y-%m-%dT%H:%M:%S.%f%zZ"),
            "replyToId": replyToId,
            "channelId": channelId,
            "recipient": recipientData,
            "conversation": conversation
            },
        headers={
            "Content-Type": "application/json"
        }
    )

# @celery_app.task
def initiateChat(data):
    membersAdded = data["membersAdded"]
    fromID = data["from"]["id"]
    generalID = data["id"]
    senderID = data["recipient"]["id"]

    if membersAdded[0]["name"] == 'Bot':
        message = 'Bot added!'
    else:
        message = 'User added!'

    respond(
        data["serviceUrl"],
        data["channelId"],
        generalID,
        {"id": senderID, "name": "Bot"},
        {"id": fromID},
        message,
        "message",
        data["conversation"])


# @celery_app.task
def respondToClient(data):
    generalID = data["id"]
    message = data["text"]
    senderID = data["recipient"]["id"]

    message = message.rstrip(".! \n\t")
    result = chatrespond(message)
    
    respond(
        data["serviceUrl"],
        data["channelId"],
        generalID,
        {"id": senderID, "name": "Bot"},
        {"id": data["from"]},
        result,
        "message",
        data["conversation"])

def chatrespond(message):
    if re.search('hi|hello|hey|howdy|hola', message, re.IGNORECASE):
        messageback = 'Hi there!'
    elif re.search('about|search', message, re.IGNORECASE):
        messageback = about(message)
    else:
        messageback = 'Come again?'
    return messageback

#####################################################################
# Begin app/bot helper and search functions
#####################################################################

# Bing search
def about(query, qtype=None):

    subscription_key = os.environ.get('BING_KEY')
    if not subscription_key:
        return "No subscription key found."

    headers = {'Ocp-Apim-Subscription-Key': subscription_key}

    params = urllib.parse.urlencode({
        # Request parameters
        'q': query,
        'count': '10',
        'offset': '0',
        'mkt': 'en-us',
        'safesearch': 'Moderate',
    })

    try:
        print("Trying a bing search")
        conn = http.client.HTTPSConnection('api.cognitive.microsoft.com')
        conn.request("GET", "/bing/v5.0/search?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        response = json.loads(str(data, 'utf-8'))
        conn.close()
    except Exception as e:
        data = "[Errno {0}] {1}".format(e.errno, e.strerror)
        response = json.loads(str(data, 'utf-8'))

    if len(response['webPages']) == 0:
        return "sorry, I don't know about " + query + \
            "\nIf you know about " + query + " please tell me."
    result = ''
    for element in response['webPages']['value']:
        try:
            print("found a result!")
            result += 'SNIPPET: %s, URL: %s\n\n' % \
                (element['snippet'], element['url'])
        except:
            pass
    return result

