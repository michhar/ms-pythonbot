from flask import Response
import json
import requests
import datetime


class Callbacks():
    """
    Holds logic with which to decorate a flask route with a callback
    function.

    TODO:
      - implement validate callback function
      - incoporate oidc for auth (if this is the right place)
    """

    def __init__(self):
        # list of obsesrvers and controllers and their info
        self.callback_map = {}

    # # @_requires_auth
    # def jsonify_callback_map(self):
    #     return jsonify([
    #         {
    #             'output': {
    #                 'id': k.split('.')[0],
    #                 'property': k.split('.')[1]
    #             },
    #             'inputs': v['inputs'],
    #             'state': v['state'],
    #             'events': v['events']
    #         } for k, v in list(self.callback_map.items())
    #     ])

    # def _validate_callback(self, output, inputs, state, events):
    #     callback_id = '{}.{}'.format(output.recipient_id,
    # output.recipient_name)

    def callback(self, output, inputs=[], state=[], events=[]):
        # self._validate_callback(output, inputs, state, events)

        callback_id = '{}.{}'.format(
            output.conversation_id, '1234'
        )
        self.callback_map[callback_id] = {
                "inputs": [
                    {
                        "type": "message",
                        "text": c.text,
                        "from": {
                            "id": c.from_id,
                            "name": c.from_name
                        },
                        "locale": "en-US",
                        "textFormat": "plain",
                        "timestamp": c.timestamp,
                        "id": c.id_var,
                        "channelId": c.channel_id,
                        "localTimestamp": c.local_timestamp,
                        "recipient": {
                            "id": c.to_id,
                            "name": c.to_name
                        },
                        "conversation": {
                            "id": c.conversation_id
                        },
                        "serviceUrl": c.service_url
                    }
                    for c in inputs
                ],
                'state': [
                    {'id': c.data_id, 'value': c.value}
                    for c in state
                ],
                'events': [
                    {'id': c.event_id, 'event': c.event}
                    for c in events
                ]
        }

        def wrap_func(func):
            def add_context(*args, **kwargs):

                output_value = func(*args, **kwargs)

                requests.post(url=output_value['url'],
                              json=output_value['json'])

                return Response(
                    json.dumps(output_value),
                    mimetype='application/json',
                    status=202
                )

            self.callback_map[callback_id]['callback'] = add_context

            return add_context

        return wrap_func


def build_response_json(service_url, channel_id, reply_to_id,
                        fromData, recipient_data, message, message_type,
                        conversation):
    """
    Input comes from the processed user input data (request)
    with a message added to it in the calling function.

    Returns a json string formatted for the Bot Framework connector.

    TODO:
      - authentication string
    """

    # if not self.auth_str:
    #     self.get_auth_str()

    url = service_url + \
        "/v3/conversations/{}/activities/{}".format(conversation["id"],
                                                    reply_to_id)

    return {
                'json': {
                        "type": message_type,
                        "text": message.strip(),
                        "locale": "en-US",
                        "from": fromData,
                        "timestamp": datetime.datetime.now()
                        .strftime("%Y-%m-%dT%H:%M:%S.%f%zZ"),
                        "localTimestamp": datetime.datetime.now()
                        .strftime("%Y-%m-%dT%H:%M:%S.%f%zZ"),
                        "replyToId": reply_to_id,
                        "channelId": channel_id,
                        "recipient": recipient_data,
                        "conversation": conversation
                    },
                'url': url
            }

###
# For the dash bot example:
###


def build_response(data, connector_type='basic'):
    """
    This function is used when a bot response is needed.

    Input is the request data from the user.  Calls a function
    to formulate the json response for the Bot Framework connector.

    Parameters
    ----------

    data : json
        The json request data from the user (with the user's message)

    connector_type : str (default: basic)
        The type of connector to be used (e.g. regex, tensorflow model, etc.)

    Returns json formatted for a response from a call out
    to build_response_json
    """

    general_id = data["id"]
    # message = data["text"]
    sender_id = data["recipient"]["id"]

    # memory = self.get_user_memory(data)

    ###
    # Place a message or connector here
    #   - something that processes 'message' from user
    ###
    if connector_type == 'basic':
        return_message = 'How can I help you today?'
    else:
        return_message = 'I need a connector.'

    return build_response_json(
        data["serviceUrl"],
        data["channelId"],
        general_id,
        {"id": sender_id, "name": "Bot"},
        {"id": data["from"]},
        return_message,
        "message",
        data["conversation"])


def build_conversation_update(data):
    """
    This function is used when a conversation update is
    needed.  (i.e. data["type"] == "conversationUpdate")

    Input is the request data from the user.  Calls a function
    to formulate the json response for the Bot Framework connector.

    Parameters
    ----------

    data : json
        The json request data

    Returns json formatted for a conversation update
    from a call out to build_response_json
    """
    members_added = data["membersAdded"]
    from_id = data["from"]["id"]
    general_id = data["id"]
    sender_id = data["recipient"]["id"]

    if members_added[0]["name"] == 'Bot':
        message = 'Bot added!'
    else:
        message = 'User added!'

    return build_response_json(
        data["serviceUrl"],
        data["channelId"],
        general_id,
        {"id": sender_id, "name": "Bot"},
        {"id": from_id},
        message,
        "message",
        data["conversation"])


class Output:
    """What data is passed back through the callback."""
    def __init__(self, url, reply_to_id, id_var, from_var,
                 from_id, from_name, conversation,
                 conversation_id, timestamp, locale,
                 recipient, recipient_id, recipient_name,
                 type_var, channel_id, local_timestamp, text):
        self.url = url
        self.reply_to_id = reply_to_id
        self.id_var = id_var
        self.from_var = from_var
        self.from_id = from_id
        self.from_name = from_name
        self.conversation = conversation
        self.conversation_id = conversation_id
        self.timestamp = timestamp
        self.locale = locale
        self.recipient = recipient
        self.recipient_id = recipient_id
        self.recipient_name = recipient_name
        self.type_var = type_var
        self.channel_id = channel_id
        self.local_timestamp = local_timestamp
        self.text = text


class Input:
    """Input data of the process/callback"""
    def __init__(self, text, from_var, from_id, from_name,
                 timestamp, id_var, channel_id, local_timestamp,
                 to_id, to_name, conversation_id, service_url):
        self.text = text
        self.from_var = from_var
        self.from_id = from_id
        self.from_name = from_name
        self.timestamp = timestamp
        self.id_var = id_var
        self.channel_id = channel_id
        self.local_timestamp = local_timestamp
        self.to_id = to_id
        self.to_name = to_name
        self.conversation_id = conversation_id
        self.service_url = service_url


class State:
    """
    State of the data of the process/callback

    TODO: incorporate (as memory?)
    """
    def __init__(self, data_id, value):
        self.data_id = data_id
        self.value = value


class Event:
    """
    Tracking of the event for this process/callback

    TODO: incorporate
    """
    def __init__(self, event_id, event):
        self.event_id = event_id
        self.event = event
