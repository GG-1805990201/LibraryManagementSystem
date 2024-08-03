from flasgger import swag_from
from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

from constants.app_constants import Roles
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'description': 'Register a new user',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'User',
                'required': ['name', 'email', 'password', 'join_date', 'role'],
                'properties': {
                    'name': {'type': 'string', 'description': 'Name of the user', 'example': 'John Doe'},
                    'email': {'type': 'string', 'description': 'Email of the user', 'example': 'john.doe@example.com'},
                    'password': {'type': 'string', 'description': 'Password for the user', 'example': 'password123'},
                    'join_date': {'type': 'string', 'format': 'date', 'description': 'Date the user joined', 'example': '2024-08-01'},
                    'role': {'type': 'string', 'description': 'Role of the user', 'example': 'Student'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User registered successfully',
            'examples': {
                'application/json': {
                    "message": "User registered successfully",
                    "user_id": 1
                }
            }
        },
        400: {
            'description': 'Invalid input'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def register():
    """Register a new user"""
    data = request.get_json()
    response, status = AuthService.register(
        data.get('name'),
        data.get('email'),
        data.get('password'),
        data.get('join_date'),
        data.get('role'),
        "current_user_email"
    )
    return make_response(jsonify(response), status)


@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'description': 'Login a user and retrieve a JWT token',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'UserLogin',
                'required': ['email', 'password'],
                'properties': {
                    'email': {'type': 'string', 'description': 'Email of the user', 'example': 'john.doe@example.com'},
                    'password': {'type': 'string', 'description': 'Password for the user', 'example': 'password123'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'User logged in successfully',
            'examples': {
                'application/json': {
                    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                }
            }
        },
        401: {
            'description': 'Invalid email or password'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def login():
    """Login a user"""
    data = request.get_json()
    response, status = AuthService.login(data.get('email'), data.get('password'))
    return jsonify(response), status


@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Auth'],
    'description': 'Access a protected endpoint',
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
            'description': 'Access to protected resource',
            'examples': {
                'application/json': {
                    "logged_in_as": "john.doe@example.com"
                }
            }
        },
        401: {
            'description': 'Missing or invalid token'
        }
    }
})
def protected():
    """Access a protected resource"""
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
