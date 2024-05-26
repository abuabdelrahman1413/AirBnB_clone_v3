#!/usr/bin/python3
"""This module defines the /places/<place_id>/amenities view
"""

from flask import jsonify, abort, request, make_response  # type: ignore
from models import storage
from api.v1.views import app_views
from models.place import Place
from models.amenity import Amenity
from os import getenv


storage_t = getenv("HBNB_TYPE_STORAGE")


@app_views.route('/places/<place_id>/amenities', strict_slashes=False,
                 methods=['GET'])
def get_amenities(place_id):
    """retrieves amenities object in a place from storage and
    displays JSON representation to it.
    """
    place = storage.get("Place", place_id)
    if place is None:
        abort(404)
    if storage_t == "db":
        amenities = place.amenities
        am_list = [amenity.to_dict() for amenity in amenities]
        return jsonify(am_list)
    else:
        amenities = place.amenity_ids
        am_list = [storage.get(Amenity, amenity_id).to_dict()
                   for amenity_id in amenities]
        return jsonify(am_list)


@app_views.route('/places/<place_id>/amenities/<amenity_id>',
                 strict_slashes=False, methods=['DELETE'])
def delete_amenity(place_id, amenity_id):
    """Deletes amenity object from a place and displays
    an empty dictionary representation.
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        abort(404)
    if amenity.place_id != place_id:
        abort(404)
    if storage_t == "db":
        storage.delete(amenity)
        storage.save()
        return make_response(jsonify({}), 200)
    else:
        place.amenity_ids.remove(amenity_id)


@app_views.route('/places/<place_id>/amenities/<amenity_id>',
                 strict_slashes=False, methods=['POST'])
def link_amenity(place_id, amenity_id):
    """Links an amenity object to a place
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        abort(404)

    if storage_t == "db":
        if amenity not in place.amenities:
            setattr(place, "amenities", amenity)
        else:
            return make_response(jsonify(amenity.to_dict()), 200)
    else:
        if amenity_id not in place.amenity_ids:
            place.amenity_ids.append(amenity_id)
        else:
            return make_response(jsonify(amenity.to_dict()), 200)
    storage.save()
    return make_response(jsonify(amenity.to_dict()), 201)
