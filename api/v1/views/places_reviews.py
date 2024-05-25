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
    if storage.get(Place, place_id) is None:
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
    if storage.get(Place, place_id) is None:
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
    if 'text' not in request.get_json():
        return make_response(jsonify({'error': 'Missing text'}), 400)
    else:
        obj_dict = request.get_json()
        new_review = Review(**obj_dict)
        new_review.place_id = place_id
        storage.new(new_review)
        storage.save()
        return make_response(jsonify(new_review.to_dict()), 201)


@app_views.route('/cities/<review_id>',
                 strict_slashes=False, methods=['PUT'])
def update_review(review_id):
    """Updates a review object with given keys and values
    """
    if storage.get(Review, review_id) is None:
        abort(404)
    try:
        request.get_json()
    except Exception:
        return make_response(jsonify({'error': 'Not a JSON'}), 400)
    obj = storage.get(Review, review_id)
    ignore = ['id', 'user_id', 'place_id', 'created_at', 'updated_at']
    for key, value in request.get_json().items():
        if key not in ignore:
            setattr(obj, key, value)
    obj.save()
    return jsonify(obj.to_dict())
