import logging

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from constants.app_constants import Roles
from services.member_service import MemberService

members_bp = Blueprint('members', __name__)


@members_bp.route('/members', methods=['GET'])
@jwt_required()
def get_members():
    current_user = get_jwt_identity()
    logging.info(f"User {current_user} is fetching members")
    return jsonify(MemberService.get_members()), 200


@members_bp.route('/members/<int:member_id>', methods=['GET'])
@jwt_required()
def get_member_by_id(member_id):
    current_user = get_jwt_identity()
    logging.info(f"User {current_user} is fetching member with id {member_id}")
    member = MemberService.get_member_by_id(member_id)
    if member:
        return jsonify(member), 200
    else:
        return jsonify({"message": "Member not found"}), 404


@members_bp.route('/members/<int:member_id>', methods=['PUT'])
@jwt_required()
def update_member(member_id):
    current_user = get_jwt_identity()
    claims = get_jwt()
    if claims['role'] != Roles.ADMIN:
        return jsonify({"message": "User not authorized to update member"}),
    logging.info(f"User {current_user} is updating member with id {member_id}")
    data = request.get_json()
    return jsonify(MemberService.update_member(member_id, data)), 200


@members_bp.route('/members/<int:member_id>', methods=['DELETE'])
@jwt_required()
def delete_member(member_id):
    current_user = get_jwt_identity()
    claims = get_jwt()
    if claims['role'] != Roles.ADMIN:
        return jsonify({"message": "User not authorized to delete member"}), 401
    logging.info(f"User {current_user} is deleting member with id {member_id}")
    return jsonify(MemberService.delete_member(member_id)), 200
