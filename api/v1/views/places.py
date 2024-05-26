#!/usr/bin/python3
"""This module defines the /places view
"""

from flask import jsonify, abort, request, make_response  # type: ignore
from models import storage
from api.v1.views import app_views
from models.state import State
from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.user import User
from os import getenv


storage_t = getenv("HBNB_TYPE_STORAGE")


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
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    try:
        obj_dict = request.get_json()
        if obj_dict is None:
            abort(400, "Not a JSON")
    except Exception:
        abort(400, "Not a JSON")
    if 'user_id' not in obj_dict:
        abort(400, "Missing user_id")
    user_id = obj_dict['user_id']
    user = storage.get(User, user_id)
    if user is None:
        abort(404)
    if 'name' not in obj_dict:
        abort(400, "Missing name")
    new_place = Place(**obj_dict)
    setattr(new_place, 'city_id', city_id)
    storage.new(new_place)
    storage.save()
    return make_response(jsonify(new_place.to_dict()), 201)


@app_views.route('/places/<place_id>',
                 strict_slashes=False, methods=['PUT'])
def update_place(place_id):
    """Updates a place object with given keys and values
    """
    obj = storage.get(Place, place_id)
    if obj is None:
        abort(404)
    try:
        obj_dict = request.get_json()
        if obj_dict is None:
            abort(400, "Not a JSON")
    except Exception:
        abort(400, "Not a JSON")
    ignore = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']
    for key, value in obj_dict.items():
        if key not in ignore:
            setattr(obj, key, value)
    storage.save()
    return jsonify(obj.to_dict())


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def search_places():
    """Searches for places with given parameters
    """
    result_pool = []
    try:
        search_param = request.get_json()
        if search_param is None:
            abort(400, "Not a JSON")
    except Exception:
        abort(400, "Not a JSON")

    if 'states' not in search_param and 'cities' not in search_param:
        result_pool = storage.all(Place).values()

    cities_id_pool = []
    if 'states' in search_param:
        if len(search_param['states']) != 0:
            for state_id in search_param['states']:
                state = storage.get(State, state_id)
                if state is None:
                    continue
                for city in state.cities:
                    cities_id_pool.append(city.id)
    if 'cities' in search_param:
        if len(search_param['cities']) != 0:
            for city in search_param['cities']:
                if city not in cities_id_pool:
                    cities_id_pool.append(city)

    for key, value in storage.all(Place).items():
        if value.city_id in cities_id_pool and value not in result_pool:
            result_pool.append(value)

    result_filtered = list(result_pool)
    if 'amenities' in search_param:
        if len(search_param['amenities']) != 0:
            for place in result_pool:
                for am_id in search_param['amenities']:
                    if storage_t == 'db':
                        am = storage.get(Amenity, am_id)
                        if am is None:
                            continue
                        if am not in place.amenities:
                            result_filtered.remove(place)
                            break
                    else:
                        if am_id not in place.amenity_ids:
                            result_filtered.remove(place)
                            break
    result_filtered = [obj.to_dict() for obj in result_filtered]
    for res_dict in result_filtered:
        if 'amenities' in res_dict:
            del res_dict['amenities']
    return jsonify(result_filtered)
