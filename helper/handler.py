import socket

from flask import jsonify

def timeout_handler(e, *args, **kwargs):
    if isinstance(e, socket.timeout):
        return jsonify({
            "status": {
                "code": 408,
                "message": "Request Timeout: The server took too long to respond."
            },
            "data": None
        }), 408