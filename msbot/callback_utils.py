from flask import Response, jsonify
import json
from time import sleep

class Callbacks():
    
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
    #     callback_id = '{}.{}'.format(output.recipient_id, output.recipient_name)

    def callback(self, output, inputs=[], state=[], events=[]):
        # self._validate_callback(output, inputs, state, events)

        callback_id = '{}.{}'.format(
            output.data_id, output.value
        )
        self.callback_map[callback_id] = {
            'inputs': [
                {'id': c.data_id, 'value': c.value}
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

                # Simulate some process
                sleep(3)

                response = { 'callback_payload' : 'everything is ok'}

                return Response(
                    json.dumps(response),
                    mimetype='application/json',
                    status=202
                    
                )

            self.callback_map[callback_id]['callback'] = add_context

            return add_context

        return wrap_func


class Output:
    """Could be some output data for this process"""
    def __init__(self, data_id, value):
        self.data_id = data_id
        self.value = value


class Input:
    """Could be some input data of the process"""
    def __init__(self, data_id, value):
        self.data_id = data_id
        self.value = value


class State:
    """Could be some state of the data of the process"""
    def __init__(self, data_id, value):
        self.data_id = rdata_id
        self.value = value


class Event:
    """Could be tracking of the event for this process"""
    def __init__(self, event_id, event):
        self.event_id = event_id
        self.event = event