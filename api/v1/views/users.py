#!/usr/bin/python3
"""This module defines the /users view
"""

from flask import jsonify, abort, request, make_response  # type: ignore
from models import storage
from api.v1.views import app_views
from models.user import User


@app_views.route('/users',
                 strict_slashes=False, methods=['GET'])
@app_views.route('/users/<user_id>',
                 strict_slashes=False, methods=['GET'])
def get_users(user_id=None):
    """retrieves users object from storage and
    displays JSON representation to it.
    """
    if (user_id is not None):
        obj = storage.get(User, user_id)
        if obj is None:
            abort(404)
        else:
            return jsonify(obj.to_dict())
    else:
        users_list = []
        for key, value in storage.all(User).items():
            users_list.append(value.to_dict())
        return jsonify(users_list)


@app_views.route('/users/<user_id>', strict_slashes=False,
                 methods=['DELETE'])
def delete_user(user_id):
    """Deletes user object from storage and displays
    an empty dictionary representation.
    """
    obj = storage.get(User, user_id)
    if obj is None:
        abort(404)
    else:
        storage.delete(obj)
        storage.save()
        return make_response(jsonify({}), 200)


@app_views.route('/users', strict_slashes=False, methods=['POST'])
def create_user():
    """Creates a new user object and adds it to storage
    with the given key value pairs.
    """
    try:
        request.get_json()
    except Exception:
        return make_response(jsonify({'error': 'Not a JSON'}), 400)
    if 'email' not in request.get_json():
        return make_response(jsonify({'error': 'Missing email'}), 400)
    if 'password' not in request.get_json():
        return make_response(jsonify({'error': 'Missing password'}), 400)
    else:
        obj_dict = request.get_json()
        new_user = User(**obj_dict)
        storage.new(new_user)
        storage.save()
        return make_response(jsonify(new_user.to_dict()), 201)


@app_views.route('/users/<user_id>',
                 strict_slashes=False, methods=['PUT'])
def update_user(user_id):
    """Updates a user object with given keys and values
    """
    if storage.get(User, user_id) is None:
        abort(404)
    try:
        request.get_json()
    except Exception:
        return make_response(jsonify({'error': 'Not a JSON'}), 400)
    obj = storage.get(User, user_id)
    for key, value in request.get_json().items():
        setattr(obj, key, value)
    obj.save()
    return jsonify(obj.to_dict())
