#!/usr/bin/python3
"""This module defines the /Review and /place_id/Review view
"""

from flask import jsonify, abort, request, make_response  # type: ignore
from models import storage
from api.v1.views import app_views
from models.place import Place
from models.review import Review
from models.user import User


@app_views.route('/places/<place_id>/reviews', strict_slashes=False,
                 methods=['GET'])
def get_reviews(place_id):
    """retrieves reviews object in a place from storage and
    displays JSON representation to it.
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    review_list = []
    for key, value in storage.all(Review).items():
        if value.place_id == place_id:
            review_list.append(value.to_dict())
    return jsonify(review_list)


@app_views.route('/reviews/<review_id>', strict_slashes=False,
                 methods=['GET'])
def get_review(review_id):
    """retrieves review object from storage and
    displays JSON representation to it.
    """
    obj = storage.get(Review, review_id)
    if obj is None:
        abort(404)
    else:
        return jsonify(obj.to_dict())


@app_views.route('/reviews/<review_id>', strict_slashes=False,
                 methods=['DELETE'])
def delete_review(review_id):
    """Deletes review object from storage and displays
    an empty dictionary representation.
    """
    obj = storage.get(Review, review_id)
    if obj is None:
        abort(404)
    else:
        storage.delete(obj)
        storage.save()
        return make_response(jsonify({}), 200)


@app_views.route('/places/<place_id>/reviews',
                 strict_slashes=False, methods=['POST'])
def create_review(place_id):
    """Creates a new review object and adds it to storage
    with the given key value pairs.
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    try:
        obj_dict = request.get_json()
        if obj_dict is None:
            abort(400, 'Not a JSON')
    except Exception:
        abort(400, 'Not a JSON')
    if 'user_id' not in obj_dict:
        abort(400, 'Missing user_id')
    user_id = obj_dict['user_id']
    user = storage.get(User, user_id)
    if user is None:
        abort(404)
    if 'text' not in obj_dict:
        abort(400, 'Missing text')
    new_review = Review(**obj_dict)
    setattr(new_review, 'place_id', place_id)
    storage.new(new_review)
    storage.save()
    return make_response(jsonify(new_review.to_dict()), 201)


@app_views.route('/reviews/<review_id>',
                 strict_slashes=False, methods=['PUT'])
def update_review(review_id):
    """Updates a review object with given keys and values
    """
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)
    try:
        obj_dict = request.get_json()
        if obj_dict is None:
            abort(400, 'Not a JSON')
    except Exception:
        abort(400, 'Not a JSON')
    ignore = ['id', 'user_id', 'place_id', 'created_at', 'updated_at']
    for key, value in obj_dict.items():
        if key not in ignore:
            setattr(review, key, value)
    storage.save()
    return jsonify(review.to_dict())
