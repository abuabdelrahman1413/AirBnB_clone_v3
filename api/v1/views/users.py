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
        obj_dict = request.get_json()
        if obj_dict is None:
            abort(400, "Not a JSON")
    except Exception:
        abort(400, "Not a JSON")
    if 'email' not in obj_dict:
        abort(400, "Missing email")
    if 'password' not in obj_dict:
        abort(400, "Missing password")
    new_user = User(**obj_dict)
    storage.new(new_user)
    storage.save()
    return make_response(jsonify(new_user.to_dict()), 201)


@app_views.route('/users/<user_id>',
                 strict_slashes=False, methods=['PUT'])
def update_user(user_id):
    """Updates a user object with given keys and values
    """
    obj = storage.get(User, user_id)
    if obj is None:
        abort(404)
    try:
        obj_dict = request.get_json()
        if obj_dict is None:
            abort(400, "Not a JSON")
    except Exception:
        abort(400, "Not a JSON")
    ket = ['id', 'email', 'created_at', 'updated_at']
    for key, value in obj_dict.items():
        if key not in ket:
            setattr(obj, key, value)
    storage.save()
    return jsonify(obj.to_dict())
