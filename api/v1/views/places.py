#!/usr/bin/python3
"""This module defines the /state view
"""

from flask import jsonify, abort, request, make_response  # type: ignore
from models import storage
from api.v1.views import app_views
from models.city import City
from models.place import Place
from models.user import User


@app_views.route('/cities/<city_id>/places', strict_slashes=False,
                 methods=['GET'])
def get_places(city_id):
    """retrieves places object in a city from storage and
    displays JSON representation to it.
    """
    if storage.get(City, city_id) is None:
        abort(404)
    places_list = []
    for key, value in storage.all(Place).items():
        if value.city_id == city_id:
            places_list.append(value.to_dict())
    return jsonify(places_list)


@app_views.route('/places/<place_id>', strict_slashes=False,
                 methods=['GET'])
def get_place(place_id):
    """retrieves place object from storage and
    displays JSON representation to it.
    """
    obj = storage.get(Place, place_id)
    if obj is None:
        abort(404)
    else:
        return jsonify(obj.to_dict())


@app_views.route('/places/<place_id>', strict_slashes=False,
                 methods=['DELETE'])
def delete_place(place_id):
    """Deletes place object from storage and displays
    an empty dictionary representation.
    """
    obj = storage.get(Place, place_id)
    if obj is None:
        abort(404)
    else:
        storage.delete(obj)
        storage.save()
        return make_response(jsonify({}), 200)


@app_views.route('/cities/<city_id>/places',
                 strict_slashes=False, methods=['POST'])
def create_place(city_id):
    """Creates a new place object and adds it to storage
    with the given key value pairs.
    """
    if storage.get(City, city_id) is None:
        abort(404)
    try:
        request.get_json()
    except Exception:
        return make_response(jsonify({'error': 'Not a JSON'}), 400)
    if 'user_id' not in request.get_json():
        return make_response(jsonify({'error': 'Missing user_id'}), 400)
    user_id = request.get_json()['user_id']
    if storage.get(User, user_id) is None:
        abort(404)
    if 'name' not in request.get_json():
        return make_response(jsonify({'error': 'Missing name'}), 400)
    else:
        obj_dict = request.get_json()
        new_place = Place(**obj_dict)
        storage.new(new_place)
        storage.save()
        return make_response(jsonify(new_place.to_dict()), 201)


@app_views.route('/places/<place_id>',
                 strict_slashes=False, methods=['PUT'])
def update_place(place_id):
    """Updates a place object with given keys and values
    """
    if storage.get(Place, place_id) is None:
        abort(404)
    try:
        request.get_json()
    except Exception:
        return make_response(jsonify({'error': 'Not a JSON'}), 400)
    obj = storage.get(Place, place_id)
    ignore = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']
    for key, value in request.get_json().items():
        if key not in ignore:
            setattr(obj, key, value)
    obj.save()
    return jsonify(obj.to_dict())
