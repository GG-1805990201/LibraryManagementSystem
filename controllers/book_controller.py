import logging

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from constants.app_constants import Roles
from services.book_service import BookService

books_bp = Blueprint('books', __name__)


@books_bp.route('/books', methods=['POST'])
@jwt_required()
def create_book():
    current_user = get_jwt_identity()
    claims = get_jwt()
    if claims['role'] != Roles.ADMIN :
        return jsonify({"message": "User not authorized to create book"}), 401
    logging.info(f"User {current_user} is creating a book")
    data = request.get_json()
    return jsonify(BookService.create_book(data)), 201


@books_bp.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    current_user = get_jwt_identity()
    logging.info(f"User {current_user} is fetching books")
    return jsonify(BookService.get_books()), 200


@books_bp.route('/books/<int:book_id>', methods=['GET'])
@jwt_required()
def get_book(book_id):
    current_user = get_jwt_identity()
    logging.info(f"User {current_user} is fetching book with id {book_id}")
    book = BookService.get_book(book_id)
    if book:
        return jsonify(book), 200
    else:
        return jsonify({"message": "Book not found"}), 404


@books_bp.route('/books/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    current_user = get_jwt_identity()
    claims = get_jwt()
    if claims['role'] != Roles.ADMIN:
        return jsonify({"message": "User not authorized to update book"}), 401
    logging.info(f"User {current_user} is updating book with id {book_id}")
    data = request.get_json()
    return jsonify(BookService.update_book(book_id, data)), 200


@books_bp.route('/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    current_user = get_jwt_identity()
    claims = get_jwt()
    if claims['role'] != Roles.ADMIN:
        return jsonify({"message": "User not authorized to delete book"}), 401
    logging.info(f"User {current_user} is deleting book with id {book_id}")
    return jsonify(BookService.delete_book(book_id)), 200
