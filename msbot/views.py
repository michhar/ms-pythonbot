#####################################################################
# Flask app for an Eliza-style bot originally and now a news bot
#  - Uses the Microsoft Bot Framework
#  - Uses Bing Search from Microsoft Cognitive Services
#  - Most code is by Ahmad Faizal B H and from his repo:
#    * https://github.com/ahmadfaizalbh/Microsoft-chatbot
#    * I've updated it to use flask instead of django :)
#####################################################################


from flask import jsonify, request, render_template, Response
import re, json, datetime, os
import requests
import jwt
from functools import wraps
import http.client, urllib.request, urllib.parse, urllib.error, base64

from msbot import app

# Our main app page/route
@app.route('/', methods=['GET', 'POST'])
def index():
    """Renders the home page which is the CNS of the web app currently, nothing pretty."""
    return render_template('index.html', title='pythonbot')


#####################################################################
# Add celery support for asynchronous calls
# (note: must also run celery worker and redis server for this example
#   to work - see README/docs)
#####################################################################

# Method for integrating celery with Flask for task queueing
from celery import Celery

def make_celery(myapp):
    celery = Celery('views', backend=myapp.config['CELERY_RESULT_BACKEND'],
                    broker=myapp.config['CELERY_BROKER_URL'])
    celery.conf.update(myapp.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with myapp.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
celery_app = make_celery(app)

#####################################################################
# Microsoft Application secrets (from BF registration process)
#####################################################################

app_client_id = os.environ.get('APP_ID', '')
app_client_secret = os.environ.get('APP_PASSWORD', '')



#####################################################################
# Create the respond function to send message back to user
#####################################################################

def respond(serviceUrl,channelId,replyToId,fromData,
            recipientData,message,messageType,conversation):

    # Authentication:  retrieving token from MSA service to help verify to BF Connector service
    url = "https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token"
    data = {"grant_type": "client_credentials",
            "client_id": app_client_id,
            "client_secret": app_client_secret,
            "scope": "https://api.botframework.com/.default"
           }
    response = requests.post(url, data)
    resData = response.json()
    try:
        authstr = "%s %s" % (resData["token_type"], resData["access_token"])
    except KeyError as err:
        authstr = ""
    
    responseURL = serviceUrl + "/v3/conversations/%s/activities/%s" % (conversation["id"],replyToId)

    requests.post(
                    url=responseURL,
                    json={
                    "type": messageType,
                    "text": message,
                    "locale": "en-US",
                    "from": fromData,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%zZ"),
                    "localTimestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%zZ"),
                    "replyToId": replyToId,
                    "channelId": channelId,
                    "recipient": recipientData,
                    "conversation": conversation
                    },
                    headers={
                        "Authorization": authstr,
                        "Content-Type": "application/json"
                    }
    )

@celery_app.task
def initiateChat(data):
    conversationID = data["conversation"]["id"]
    membersAdded=data["membersAdded"]
    fromID = data["from"]["id"]
    generalID = data["id"]
    message = 'Welcome to my news app!'
    senderID = data["recipient"]["id"]

    respond(
        data["serviceUrl"],
            data["channelId"],
            generalID,
            {"id": senderID, "name": "Bot"},
            {"id": fromID},
            message,
            "message",
            data["conversation"])

@celery_app.task
def respondToClient(data):
    conversationID = data["conversation"]["id"]
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
    if re.search('hi|hello|hey|howdy|hola', message):
        messageback = 'Hi there!'
    else:
        messageback = 'Come again?'
    return messageback


#####################################################################
# Authentication method/wrapper with JWT tokens
#####################################################################

def jwt_authenticate(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        auth_token = auth.replace('Bearer ', '')

        if app.config['DEBUG']:
            open_id_json_url = 'https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration'
            options = {'verify_signature': True,
                       'verify_aud': False,
                       'verify_iat': True, 'verify_exp': True,
                       'verify_nbf': True, 'verify_iss': True,
                       'verify_sub': True, 'verify_jti': True}
        else:
            open_id_json_url = 'https://login.botframework.com/v1/.well-known/openidconfiguration'
            options = {'verify_signature': True,
                       'verify_aud': False,
                       'verify_iat': True, 'verify_exp': True,
                       'verify_nbf': True, 'verify_iss': True,
                       'verify_sub': True, 'verify_jti': True}
        req = requests.get(open_id_json_url)
        data = req.json()

        jwks_uri = data['jwks_uri']
        req = requests.get(jwks_uri)
        data = req.json()
        keys = data.get('keys')
        valid = False
        for key in keys:
            try:
                results = jwt.decode(auth_token, key=key, algorithms='RS256',
                                     audience=app_client_id,
                                     options=options)
                valid = True
                break
            except:
                pass

        if not valid:
            return Response('JWT Token Invalid', 401, {'WWWAuthenticate':'Basic realm="Login Required"'})

        return f(*args, **kwargs)
    return decorated


#####################################################################
# Main route for messaging
#####################################################################

@app.route('/api/messages', methods=['POST', 'GET'])
@jwt_authenticate
def messages():
    if request.method=="POST":
        # User message to bot
        data = request.json

        # Async methods run as tasks with celery backend
        if data["type"]=="conversationUpdate":
            # Add the members to the conversation
            initiateChat.delay(data)
        else:
            # The bot responds to the user
            respondToClient.delay(data)

        return Response(
            mimetype='application/json',
            status=202
        )
    return jsonify({'message': "Invalid request method"}), 405

@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


#####################################################################
# Begin app/bot helper and search functions
#####################################################################


# Bing search
def about(query,qtype=None):

    try:
        subscription_key = os.environ['BING_KEY']
    except KeyError as err:
        return "No subscription key found.  %s" % err


    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': subscription_key,
    }

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
        # result = json.dumps(result, indent=4, sort_keys=True)
        conn.close()
    except Exception as e:
        data = "[Errno {0}] {1}".format(e.errno, e.strerror)
        response = json.loads(str(data, 'utf-8'))


    if len(response['webPages']) == 0:
        return "sorry, I don't know about " + query + "\nIf you know about "+ query + " please tell me."
    result = ""
    if len(response['webPages']) == 1:
        print("found a result!")
        if "detailedDescription" in response['webPages'][0]['value']:
            return response['webPages'][0]['value']['url']
        else:
            return response['webPages'][0]['value']['url'] +" snippet: " +\
                   response['webPages'][0]['value']["snippet"]
    for element in response['webPages']:
      try:
          print("found a result!")
          result += element['value']['url'] + "->" +element['value']["snippet"]+"\n"
      except:pass
    print(response)
    return response



