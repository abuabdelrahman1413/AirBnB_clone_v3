#!/usr/bin/python3
""" Index Module """

from flask import jsonify
from api.v1.views import app_views


@app_views.route('/status')
def status():
    """ Status message """
    return jsonify({"status": "OK"})
