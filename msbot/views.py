"""
Flask app for testing the OpenID Connect extension.
"""
from flask import jsonify, request

from msbot import app, app_backend, oidc
from .callback_utils import Input, Output
from .callback_utils import build_response, build_conversation_update

#####################################################################
# Main routes for messaging
#####################################################################


@app.route('/')
@oidc.accept_token()
def index():
    """
    Main route.
    Here, used for testing a web app is working.
    """

    return jsonify({'message': 'too many secrets'}), 200, {
        'Content-Type': 'application/json'
    }


@app.route('/api/messages', methods=['POST', 'GET'])
@oidc.accept_token()
@app_backend.callback(Output('url',
                             'reply_to_id',
                             'id_var',
                             'from_var',
                             'from_id',
                             'from_name',
                             'conversation',
                             'conversation_id',
                             'timestamp',
                             'locale',
                             'recipient',
                             'recipient_id',
                             'recipient_name',
                             'type',
                             'channel_id',
                             'local_timestamp',
                             'text'),
                      [Input('text',  # appears to work
                             'from_var',
                             'from_id',
                             'from_name',
                             'timestamp',
                             'id_var',
                             'channel_id',
                             'local_timestamp',
                             'to_id',
                             'to_name',
                             'conversation_id',
                             'service_url')])
def messages():
    """Method to capture posted message data from a user
    and respond."""

    if request.method == "POST":
        data = request.json

        if data["type"] == "conversationUpdate":
            # Add the members to the conversation
            message_back = build_conversation_update(data=data)
        else:
            # The bot responds to the user
            message_back = build_response(data=data, connector_type='basic')

        return message_back

    return jsonify({'message': "Invalid request method"}), 405, {
        'Content-Type': 'application/json'
    }
