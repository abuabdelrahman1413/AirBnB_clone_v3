#!/usr/bin/python3
"""This module defines the /amenities view
"""

from flask import jsonify, abort, request, make_response  # type: ignore
from models import storage
from api.v1.views import app_views
from models.amenity import Amenity


@app_views.route('/amenities',
                 strict_slashes=False, methods=['GET'])
@app_views.route('/amenities/<amenity_id>',
                 strict_slashes=False, methods=['GET'])
def get_amenities(amenity_id=None):
    """retrieves amenities object from storage and
    displays JSON representation to it.
    """
    if (amenity_id is not None):
        obj = storage.get(Amenity, amenity_id)
        if obj is None:
            abort(404)
        else:
            return jsonify(obj.to_dict())
    else:
        amenities_list = []
        for key, value in storage.all(Amenity).items():
            amenities_list.append(value.to_dict())
        return jsonify(amenities_list)


@app_views.route('/amenities/<amenity_id>', strict_slashes=False,
                 methods=['DELETE'])
def delete_amenity(amenity_id):
    """Deletes amenity object from storage and displays
    an empty dictionary representation.
    """
    obj = storage.get(Amenity, amenity_id)
    if obj is None:
        abort(404)
    else:
        storage.delete(obj)
        storage.save()
        return make_response(jsonify({}), 200)


@app_views.route('/amenities', strict_slashes=False, methods=['POST'])
def create_amenity():
    """Creates a new amenity object and adds it to storage
    with the given key value pairs.
    """
    try:
        request.get_json()
    except Exception:
        return make_response(jsonify({'error': 'Not a JSON'}), 400)
    if 'name' not in request.get_json():
        return make_response(jsonify({'error': 'Missing name'}), 400)
    else:
        obj_dict = request.get_json()
        new_amenity = Amenity(**obj_dict)
        storage.new(new_amenity)
        storage.save()
        return make_response(jsonify(new_amenity.to_dict()), 201)


@app_views.route('/amenities/<amenity_id>', strict_slashes=False, methods=['PUT'])
def update_amenity(amenity_id):
    """Updates a amenity object with given keys and values
    """
    if storage.get(Amenity, amenity_id) is None:
        abort(404)
    try:
        request.get_json()
    except Exception:
        return make_response(jsonify({'error': 'Not a JSON'}), 400)
    obj = storage.get(Amenity, amenity_id)
    for key, value in request.get_json().items():
        setattr(obj, key, value)
    obj.save()
    return jsonify(obj.to_dict())
