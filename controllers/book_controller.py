import logging
from flasgger import swag_from
from flask import Blueprint, request, jsonify, make_response, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from constants.app_constants import Roles
from services.book_service import BookService

books_bp = Blueprint('books', __name__)

@books_bp.route('/books', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Books'],
    'description': 'Create a new book',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token (Bearer <token>)'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'Book',
                'required': [
                    'title', 'author', 'published_date', 'isbn', 'number_of_pages', 'language', 'available_copies'
                ],
                'properties': {
                    'title': {'type': 'string', 'description': 'The title of the book', 'example': 'The Great Gatsby'},
                    'author': {'type': 'string', 'description': 'The author of the book', 'example': 'F. Scott Fitzgerald'},
                    'published_date': {'type': 'string', 'format': 'date', 'description': 'The date the book was published', 'example': '1925-04-10'},
                    'isbn': {'type': 'string', 'description': 'The ISBN of the book', 'example': '9780743273565'},
                    'number_of_pages': {'type': 'integer', 'description': 'The number of pages in the book', 'example': 180},
                    'cover_image': {'type': 'string', 'description': 'URL to the cover image of the book', 'example': 'http://example.com/covers/great-gatsby.jpg'},
                    'language': {'type': 'string', 'description': 'The language of the book', 'example': 'English'},
                    'available_copies': {'type': 'integer', 'description': 'Number of available copies of the book', 'example': 5}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Book created successfully',
            'examples': {
                'application/json': {
                    "message": "Book added successfully",
                    "book_id": 1
                }
            }
        },
        403: {
            'description': 'User not authorized to create book'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def create_book():
    current_user = get_jwt_identity()
    claims = get_jwt()
    if claims['role'] != Roles.ADMIN:
        return make_response(jsonify({"message": "User not authorized to create book"}), 403)
    logging.info(f"User {current_user} is creating a book")
    data = request.get_json()
    try:
        response = BookService.create_book(data)
        book_id = response.get('book_id')  # Assuming response returns a book_id
        response["_links"] = {
            "self": url_for('books.get_book', book_id=book_id, _external=True),
            "update": {
                "href": url_for('books.update_book', book_id=book_id, _external=True),
                "method": "PUT"
            },
            "delete": {
                "href": url_for('books.delete_book', book_id=book_id, _external=True),
                "method": "DELETE"
            },
            "list": url_for('books.get_books', _external=True)
        }
        return make_response(jsonify(response), 201)
    except Exception as e:
        logging.error(f"Error creating book: {str(e)}")
        return make_response(jsonify({"message": "Internal server error"}), 500)


@books_bp.route('/books', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Books'],
    'description': 'Get list of books with filtering and pagination',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token (Bearer <token>)'
        },
        {'name': 'author', 'in': 'query', 'type': 'string', 'description': 'Filter books by author'},
        {'name': 'published_start', 'in': 'query', 'type': 'string', 'format': 'date', 'description': 'Filter books published after this date'},
        {'name': 'published_end', 'in': 'query', 'type': 'string', 'format': 'date', 'description': 'Filter books published before this date'},
        {'name': 'search', 'in': 'query', 'type': 'string', 'description': 'Search books by title or author'},
        {'name': 'page', 'in': 'query', 'type': 'integer', 'default': 1, 'description': 'Page number for pagination'},
        {'name': 'limit', 'in': 'query', 'type': 'integer', 'default': 10, 'description': 'Number of results per page for pagination'},
    ],
    'responses': {
        200: {
            'description': 'List of books',
            'examples': {
                'application/json': {
                    "books": [
                        {
                            "id": 1,
                            "title": "The Great Gatsby",
                            "author": "F. Scott Fitzgerald",
                            "published_date": "1925-04-10",
                            "isbn": "9780743273565",
                            "number_of_pages": 180,
                            "cover_image": "http://example.com/covers/great-gatsby.jpg",
                            "language": "English",
                            "available_copies": 5
                        }
                    ],
                    "total": 1,
                    "page": 1,
                    "limit": 10,
                    "next_page": None,
                    "prev_page": None,
                    "_links": {
                        "self": "http://localhost:5000/books?page=1&limit=10",
                        "create": {
                            "href": "http://localhost:5000/books",
                            "method": "POST"
                        }
                    }
                }
            }
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def get_books():
    current_user = get_jwt_identity()
    logging.info(f"User {current_user} is fetching books")

    # Retrieve query parameters for filtering and pagination
    author = request.args.get('author')
    published_start = request.args.get('published_start')
    published_end = request.args.get('published_end')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    search = request.args.get('search')

    try:
        books, total = BookService.get_books(author, published_start, published_end, page, limit, search)

        # Prepare pagination information
        next_page = url_for('books.get_books', author=author, published_start=published_start, published_end=published_end,
                            page=page + 1, limit=limit, _external=True) if page * limit < total else None
        prev_page = url_for('books.get_books', author=author, published_start=published_start, published_end=published_end,
                            page=page - 1, limit=limit, _external=True) if page > 1 else None

        # Add HATEOAS links to each book
        books_with_links = []
        for book in books:
            book_dict = dict(book)
            book_dict["_links"] = {
                "self": url_for('books.get_book', book_id=book['id'], _external=True),
                "update": {
                    "href": url_for('books.update_book', book_id=book['id'], _external=True),
                    "method": "PUT"
                },
                "delete": {
                    "href": url_for('books.delete_book', book_id=book['id'], _external=True),
                    "method": "DELETE"
                }
            }
            books_with_links.append(book_dict)

        # Prepare response with HATEOAS links
        response = {
            "books": books_with_links,
            "total": total,
            "page": page,
            "limit": limit,
            "next_page": next_page,
            "prev_page": prev_page,
            "_links": {
                "self": url_for('books.get_books', page=page, limit=limit, author=author,
                                published_start=published_start, published_end=published_end, _external=True),
                "create": {
                    "href": url_for('books.create_book', _external=True),
                    "method": "POST"
                }
            }
        }

        return make_response(jsonify(response), 200)
    except Exception as e:
        logging.error(f"Error fetching books: {str(e)}")
        return make_response(jsonify({"message": "Internal server error"}), 500)


@books_bp.route('/books/<int:book_id>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Books'],
    'description': 'Get details of a specific book by its ID',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token (Bearer <token>)'
        },
        {'name': 'book_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': 'The book identifier'}
    ],
    'responses': {
        200: {
            'description': 'Book details',
            'examples': {
                'application/json': {
                    "id": 1,
                    "title": "The Great Gatsby",
                    "author": "F. Scott Fitzgerald",
                    "published_date": "1925-04-10",
                    "isbn": "9780743273565",
                    "number_of_pages": 180,
                    "cover_image": "http://example.com/covers/great-gatsby.jpg",
                    "language": "English",
                    "available_copies": 5
                }
            }
        },
        404: {
            'description': 'Book not found'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def get_book(book_id):
    current_user = get_jwt_identity()
    logging.info(f"User {current_user} is fetching book with id {book_id}")
    try:
        book = BookService.get_book(book_id)
        if book:
            book["_links"] = {
                "self": url_for('books.get_book', book_id=book_id, _external=True),
                "update": {
                    "href": url_for('books.update_book', book_id=book_id, _external=True),
                    "method": "PUT"
                },
                "delete": {
                    "href": url_for('books.delete_book', book_id=book_id, _external=True),
                    "method": "DELETE"
                },
                "list": url_for('books.get_books', _external=True)
            }
            return make_response(jsonify(book), 200)
        else:
            return make_response(jsonify({"message": "Book not found"}), 404)
    except Exception as e:
        logging.error(f"Error fetching book with id {book_id}: {str(e)}")
        return make_response(jsonify({"message": "Internal server error"}), 500)


@books_bp.route('/books/<int:book_id>', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['Books'],
    'description': 'Update the details of a specific book by its ID',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token (Bearer <token>)'
        },
        {'name': 'book_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': 'The book identifier'},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'BookUpdate',
                'properties': {
                    'title': {'type': 'string', 'description': 'The title of the book', 'example': 'The Great Gatsby'},
                    'author': {'type': 'string', 'description': 'The author of the book', 'example': 'F. Scott Fitzgerald'},
                    'published_date': {'type': 'string', 'format': 'date', 'description': 'The date the book was published', 'example': '1925-04-10'},
                    'isbn': {'type': 'string', 'description': 'The ISBN of the book', 'example': '9780743273565'},
                    'number_of_pages': {'type': 'integer', 'description': 'The number of pages in the book', 'example': 180},
                    'cover_image': {'type': 'string', 'description': 'URL to the cover image of the book', 'example': 'http://example.com/covers/great-gatsby.jpg'},
                    'language': {'type': 'string', 'description': 'The language of the book', 'example': 'English'},
                    'available_copies': {'type': 'integer', 'description': 'Number of available copies of the book', 'example': 5}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Book updated successfully',
            'examples': {
                'application/json': {
                    "message": "Book updated successfully"
                }
            }
        },
        403: {
            'description': 'User not authorized to update book'
        },
        404: {
            'description': 'Book not found'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def update_book(book_id):
    current_user = get_jwt_identity()
    claims = get_jwt()
    if claims['role'] != Roles.ADMIN:
        return make_response(jsonify({"message": "User not authorized to update book"}), 403)
    logging.info(f"User {current_user} is updating book with id {book_id}")
    data = request.get_json()
    try:
        response = BookService.update_book(book_id, data)
        response["_links"] = {
            "self": url_for('books.get_book', book_id=book_id, _external=True),
            "delete": {
                "href": url_for('books.delete_book', book_id=book_id, _external=True),
                "method": "DELETE"
            },
            "list": url_for('books.get_books', _external=True)
        }
        return make_response(jsonify(response), 200)
    except Exception as e:
        logging.error(f"Error updating book with id {book_id}: {str(e)}")
        return make_response(jsonify({"message": "Internal server error"}), 500)


@books_bp.route('/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
@swag_from({
    'tags': ['Books'],
    'description': 'Delete a specific book by its ID',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token (Bearer <token>)'
        },
        {'name': 'book_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': 'The book identifier'}
    ],
    'responses': {
        200: {
            'description': 'Book deleted successfully',
            'examples': {
                'application/json': {
                    "message": "Book deleted successfully"
                }
            }
        },
        403: {
            'description': 'User not authorized to delete book'
        },
        404: {
            'description': 'Book not found'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def delete_book(book_id):
    current_user = get_jwt_identity()
    claims = get_jwt()
    if claims['role'] != Roles.ADMIN:
        return make_response(jsonify({"message": "User not authorized to delete book"}), 403)
    logging.info(f"User {current_user} is deleting book with id {book_id}")
    try:
        response = BookService.delete_book(book_id)
        response["_links"] = {
            "list": url_for('books.get_books', _external=True)
        }
        return make_response(jsonify(response), 200)
    except Exception as e:
        logging.error(f"Error deleting book with id {book_id}: {str(e)}")
        return make_response(jsonify({"message": "Internal server error"}), 500)
