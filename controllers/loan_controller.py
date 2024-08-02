import logging

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from constants.app_constants import Roles
from services.loan_service import LoanService

loans_bp = Blueprint('loans', __name__)


@loans_bp.route('/loans', methods=['POST'])
@jwt_required()
def create_loan():
    current_user = get_jwt_identity()
    claims = get_jwt()
    if claims['role'] != Roles.ADMIN:
        return jsonify({"message": "User not authorized to create loan"}), 401
    logging.info(f"User {current_user} is creating a loan")
    data = request.get_json()
    response, status = LoanService.create_loan(data)
    return jsonify(response), status


@loans_bp.route('/loans', methods=['GET'])
@jwt_required()
def get_loans():
    return jsonify(LoanService.get_loans()), 200


@loans_bp.route('/loans/<int:loan_id>', methods=['GET'])
@jwt_required()
def get_loan(loan_id):
    loan = LoanService.get_loan(loan_id)
    if loan:
        return jsonify(loan), 200
    else:
        return jsonify({"message": "Loan not found"}), 404


@loans_bp.route('/loans/<int:loan_id>', methods=['PUT'])
@jwt_required()
def update_loan(loan_id):
    current_user = get_jwt_identity()
    claims = get_jwt()
    if claims['role'] != Roles.ADMIN:
        return jsonify({"message": "User not authorized to update loan"}), 401
    logging.info(f"User {current_user} is updating loan with id {loan_id}")
    data = request.get_json()
    response, status = LoanService.update_loan(loan_id, data)
    return jsonify(response), status


@loans_bp.route('/loans/<int:loan_id>', methods=['DELETE'])
@jwt_required()
def delete_loan(loan_id):
    current_user = get_jwt_identity()
    claims = get_jwt()
    if claims['role'] != Roles.ADMIN:
        return jsonify({"message": "User not authorized to delete the loan"}), 401
    logging.info(f"User {current_user} is deleting loan with id {loan_id}")
    response, status = LoanService.delete_loan(loan_id)
    return jsonify(response), status
