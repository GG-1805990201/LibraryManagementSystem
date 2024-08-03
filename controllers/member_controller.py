import logging
from flasgger import swag_from
from flask import Blueprint, request, jsonify, make_response, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from constants.app_constants import Roles
from services.member_service import MemberService

members_bp = Blueprint('members', __name__)

@members_bp.route('/members', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Members'],
    'description': 'Retrieve a list of all members',
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
            'description': 'List of members',
            'examples': {
                'application/json': {
                    "members": [
                        {
                            "id": 1,
                            "name": "John Doe",
                            "email": "john.doe@example.com",
                            "join_date": "2023-01-01",
                            "_links": {
                                "self": "http://localhost:5000/members/1",
                                "update": {
                                    "href": "http://localhost:5000/members/1",
                                    "method": "PUT"
                                },
                                "delete": {
                                    "href": "http://localhost:5000/members/1",
                                    "method": "DELETE"
                                }
                            }
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
def get_members():
    try:
        current_user = get_jwt_identity()
        logging.info(f"User {current_user} is trying to get all members")
        members = MemberService.get_members()
        members_with_links = []
        for member in members:
            member_dict = dict(member)
            member_dict["_links"] = {
                "self": url_for('members.get_member_by_id', member_id=member['id'], _external=True),
                "update": {
                    "href": url_for('members.update_member', member_id=member['id'], _external=True),
                    "method": "PUT"
                },
                "delete": {
                    "href": url_for('members.delete_member', member_id=member['id'], _external=True),
                    "method": "DELETE"
                }
            }
            members_with_links.append(member_dict)
        return make_response(jsonify({"members": members_with_links}), 200)

    except Exception as e:
        logging.error(f"Error fetching members: {str(e)}")
        return make_response(jsonify({"message": "Internal server error"}), 500)


@members_bp.route('/members/<int:member_id>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Members'],
    'description': 'Retrieve details of a specific member by their ID',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token (Bearer <token>)'
        },
        {'name': 'member_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': 'The member identifier'}
    ],
    'responses': {
        200: {
            'description': 'Member details',
            'examples': {
                'application/json': {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "join_date": "2023-01-01",
                    "_links": {
                        "self": "http://localhost:5000/members/1",
                        "update": {
                            "href": "http://localhost:5000/members/1",
                            "method": "PUT"
                        },
                        "delete": {
                            "href": "http://localhost:5000/members/1",
                            "method": "DELETE"
                        },
                        "list": "http://localhost:5000/members"
                    }
                }
            }
        },
        404: {
            'description': 'Member not found'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def get_member_by_id(member_id):
    try:
        current_user = get_jwt_identity()
        logging.info(f"User {current_user} is trying to get member {member_id}")
        member = MemberService.get_member_by_id(member_id)
        if member:
            member_dict = dict(member)
            member_dict["_links"] = {
                "self": url_for('members.get_member_by_id', member_id=member_id, _external=True),
                "update": {
                    "href": url_for('members.update_member', member_id=member_id, _external=True),
                    "method": "PUT"
                },
                "delete": {
                    "href": url_for('members.delete_member', member_id=member_id, _external=True),
                    "method": "DELETE"
                },
                "list": url_for('members.get_members', _external=True)
            }
            return make_response(jsonify(member_dict), 200)
        else:
            return make_response(jsonify({"message": "Member not found"}), 404)
    except Exception as e:
        logging.error(f"Error fetching member with id {member_id}: {str(e)}")
        return make_response(jsonify({"message": "Internal server error"}), 500)


@members_bp.route('/members/<int:member_id>', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['Members'],
    'description': 'Update the details of a specific member by their ID',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token (Bearer <token>)'
        },
        {'name': 'member_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': 'The member identifier'},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'MemberUpdate',
                'properties': {
                    'name': {'type': 'string', 'description': 'The name of the member', 'example': 'John Doe'},
                    'email': {'type': 'string', 'description': 'The email of the member', 'example': 'john.doe@example.com'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Member updated successfully',
            'examples': {
                'application/json': {
                    "message": "Member updated successfully"
                }
            }
        },
        403: {
            'description': 'User not authorized to update member'
        },
        404: {
            'description': 'Member not found'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def update_member(member_id):
    data = request.get_json()
    current_user = get_jwt_identity()
    claims = get_jwt()

    # Check if the user has the 'ADMIN' role
    if claims['role'] != Roles.ADMIN:
        logging.warning(f"User {current_user} attempted to update member {member_id} without permission.")
        return make_response(jsonify({"message": "User not authorized to update member"}), 403)
    try:
        response = MemberService.update_member(member_id, data)
        return make_response(jsonify(response), 200)
    except Exception as e:
        logging.error(f"Error updating member with id {member_id}: {str(e)}")
        return make_response(jsonify({"message": "Internal server error"}), 500)


@members_bp.route('/members/<int:member_id>', methods=['DELETE'])
@jwt_required()
@swag_from({
    'tags': ['Members'],
    'description': 'Delete a specific member by their ID',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token (Bearer <token>)'
        },
        {'name': 'member_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': 'The member identifier'}
    ],
    'responses': {
        200: {
            'description': 'Member deleted successfully',
            'examples': {
                'application/json': {
                    "message": "Member deleted successfully"
                }
            }
        },
        403: {
            'description': 'User not authorized to delete member'
        },
        404: {
            'description': 'Member not found'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def delete_member(member_id):
    try:
        current_user = get_jwt_identity()
        claims = get_jwt()
        if claims['role'] != Roles.ADMIN:
            logging.warning(f"User {current_user} attempted to delete member {member_id} without permission.")
            return make_response(jsonify({"message": "User not authorized to delete member"}), 403)
        response = MemberService.delete_member(member_id)
        return make_response(jsonify(response), 200)
    except Exception as e:
        logging.error(f"Error deleting member with id {member_id}: {str(e)}")
        return make_response(jsonify({"message": "Internal server error"}), 500)
