from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt

from constants.app_constants import Roles
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    data = request.get_json()
    current_user_email = get_jwt_identity()
    claims = get_jwt()
    if claims['role'] != Roles.ADMIN:
        return jsonify({"message": "User not authorized to add new member"}), 401
    return jsonify(
        AuthService.register(data.get('name'), data.get('email'), data.get('password'), data.get('join_date'),
                             data.get('role'), current_user_email)), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    response, status = AuthService.login(data.get('email'), data.get('password'))
    return jsonify(response), status


@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
