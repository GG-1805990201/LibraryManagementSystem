import logging
from flasgger import swag_from
from flask import Blueprint, request, jsonify, make_response, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from constants.app_constants import Roles
from services.loan_service import LoanService

loans_bp = Blueprint('loans', __name__)


@loans_bp.route('/loans', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Loans'],
    'description': 'Create a new loan',
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
                'id': 'Loan',
                'required': ['book_id', 'member_id', 'loan_date'],
                'properties': {
                    'book_id': {'type': 'integer', 'description': 'The ID of the book being loaned', 'example': 1},
                    'member_id': {'type': 'integer', 'description': 'The ID of the member taking the loan', 'example': 1},
                    'loan_date': {'type': 'string', 'format': 'date', 'description': 'The date the loan was made', 'example': '2024-08-01'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Loan created successfully',
            'examples': {
                'application/json': {
                    "message": "Loan created successfully",
                    "loan_id": 1
                }
            }
        },
        403: {
            'description': 'User not authorized to create loan'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def create_loan():
    current_user = get_jwt_identity()
    claims = get_jwt()
    if claims['role'] != Roles.ADMIN:
        return make_response(jsonify({"message": "User not authorized to create loan"}), 403)
    logging.info(f"User {current_user} is creating a loan")
    data = request.get_json()
    try:
        response, status = LoanService.create_loan(data)
        if status == 201:
            loan_id = response.get('loan_id')
            response["_links"] = {
                "self": url_for('loans.get_loan', loan_id=loan_id, _external=True),
                "update": {
                    "href": url_for('loans.update_loan', loan_id=loan_id, _external=True),
                    "method": "PUT"
                },
                "delete": {
                    "href": url_for('loans.delete_loan', loan_id=loan_id, _external=True),
                    "method": "DELETE"
                },
                "list": {
                    "href": url_for('loans.get_loans', _external=True),
                    "method": "GET"
                }
            }
        return make_response(jsonify(response), status)
    except Exception as e:
        logging.error(f"Error creating loan: {str(e)}")
        return make_response(jsonify({"message": "Internal server error"}), 500)


@loans_bp.route('/loans', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Loans'],
    'description': 'Retrieve a list of all loan records',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token (Bearer <token>)'
        }
    ],
    'responses': {
        200: {
            'description': 'List of loans',
            'examples': {
                'application/json': {
                    "loans": [
                        {
                            "id": 1,
                            "book_id": 1,
                            "member_id": 1,
                            "loan_date": "2024-08-01",
                            "return_date": "2024-08-16",
                            "actual_return_date": None,
                            "fine": 0
                        }
                    ]
                }
            }
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def get_loans():
    try:
        loans = LoanService.get_loans()
        loans_with_links = []
        for loan in loans:
            loan_dict = dict(loan)
            loan_dict["_links"] = {
                "self": url_for('loans.get_loan', loan_id=loan['id'], _external=True),
                "update": {
                    "href": url_for('loans.update_loan', loan_id=loan['id'], _external=True),
                    "method": "PUT"
                },
                "delete": {
                    "href": url_for('loans.delete_loan', loan_id=loan['id'], _external=True),
                    "method": "DELETE"
                }
            }
            loans_with_links.append(loan_dict)
        return make_response(jsonify({"loans": loans_with_links}), 200)
    except Exception as e:
        logging.error(f"Error fetching loans: {str(e)}")
        return make_response(jsonify({"message": "Internal server error"}), 500)


@loans_bp.route('/loans/<int:loan_id>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Loans'],
    'description': 'Retrieve details of a specific loan by its ID',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token (Bearer <token>)'
        },
        {'name': 'loan_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': 'The loan identifier'}
    ],
    'responses': {
        200: {
            'description': 'Loan details',
            'examples': {
                'application/json': {
                    "id": 1,
                    "book_id": 1,
                    "member_id": 1,
                    "loan_date": "2024-08-01",
                    "return_date": "2024-08-16",
                    "actual_return_date": None,
                    "fine": 0
                }
            }
        },
        404: {
            'description': 'Loan not found'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def get_loan(loan_id):
    try:
        loan = LoanService.get_loan(loan_id)
        if loan:
            loan["_links"] = {
                "self": url_for('loans.get_loan', loan_id=loan_id, _external=True),
                "update": {
                    "href": url_for('loans.update_loan', loan_id=loan_id, _external=True),
                    "method": "PUT"
                },
                "delete": {
                    "href": url_for('loans.delete_loan', loan_id=loan_id, _external=True),
                    "method": "DELETE"
                },
                "list": {
                    "href": url_for('loans.get_loans', _external=True),
                    "method": "GET"
                }
            }
            return make_response(jsonify(loan), 200)
        else:
            return make_response(jsonify({"message": "Loan not found"}), 404)
    except Exception as e:
        logging.error(f"Error fetching loan with id {loan_id}: {str(e)}")
        return make_response(jsonify({"message": "Internal server error"}), 500)


@loans_bp.route('/loans/<int:loan_id>', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['Loans'],
    'description': 'Update the details of a specific loan by its ID',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token (Bearer <token>)'
        },
        {'name': 'loan_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': 'The loan identifier'},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'LoanUpdate',
                'properties': {
                    'return_date': {'type': 'string', 'format': 'date', 'description': 'The return date for the loan', 'example': '2024-08-16'},
                    'actual_return_date': {'type': 'string', 'format': 'date', 'description': 'The actual return date for the loan', 'example': '2024-08-16'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Loan updated successfully',
            'examples': {
                'application/json': {
                    "message": "Loan updated successfully"
                }
            }
        },
        403: {
            'description': 'User not authorized to update loan'
        },
        404: {
            'description': 'Loan not found'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def update_loan(loan_id):
    current_user = get_jwt_identity()
    claims = get_jwt()
    if claims['role'] != Roles.ADMIN:
        return make_response(jsonify({"message": "User not authorized to update loan"}), 403)
    logging.info(f"User {current_user} is updating loan with id {loan_id}")
    data = request.get_json()
    try:
        response, status = LoanService.update_loan(loan_id, data)
        if status == 200:
            response["_links"] = {
                "self": url_for('loans.get_loan', loan_id=loan_id, _external=True),
                "delete": {
                    "href": url_for('loans.delete_loan', loan_id=loan_id, _external=True),
                    "method": "DELETE"
                },
                "list": {
                    "href": url_for('loans.get_loans', _external=True),
                    "method": "GET"
                }
            }
        return make_response(jsonify(response), status)
    except Exception as e:
        logging.error(f"Error updating loan with id {loan_id}: {str(e)}")
        return make_response(jsonify({"message": "Internal server error"}), 500)


@loans_bp.route('/loans/<int:loan_id>', methods=['DELETE'])
@jwt_required()
@swag_from({
    'tags': ['Loans'],
    'description': 'Delete a specific loan by its ID',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token (Bearer <token>)'
        },
        {'name': 'loan_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': 'The loan identifier'}
    ],
    'responses': {
        200: {
            'description': 'Loan deleted successfully',
            'examples': {
                'application/json': {
                    "message": "Loan deleted successfully"
                }
            }
        },
        403: {
            'description': 'User not authorized to delete loan'
        },
        404: {
            'description': 'Loan not found'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def delete_loan(loan_id):
    current_user = get_jwt_identity()
    claims = get_jwt()
    if claims['role'] != Roles.ADMIN:
        return make_response(jsonify({"message": "User not authorized to delete the loan"}), 403)
    logging.info(f"User {current_user} is deleting loan with id {loan_id}")
    try:
        response, status = LoanService.delete_loan(loan_id)
        if status == 200:
            response["_links"] = {
                "list": {
                    "href": url_for('loans.get_loans', _external=True),
                    "method": "GET"
                }
            }
        return make_response(jsonify(response), status)
    except Exception as e:
        logging.error(f"Error deleting loan with id {loan_id}: {str(e)}")
        return make_response(jsonify({"message": "Internal server error"}), 500)
