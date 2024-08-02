import logging

from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from config.sqlite_config import get_db_connection
from dao.member_dao_queries import MemberDaoQueries
from dao.user_dao_queries import UserDaoQueries


class AuthService:
    @staticmethod
    def register(name, email, password, join_date,role,current_user_email):
        logging.info(f"User {current_user_email} is trying to register a new user")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(MemberDaoQueries.insert_new_member(), (name, email, join_date))
        member_id = cursor.lastrowid

        password_hash = generate_password_hash(password)
        cursor.execute(UserDaoQueries.insert_new_user(), (member_id, email, password_hash,role))

        conn.commit()
        conn.close()

        return {"message": "User registered successfully by "+current_user_email+" as "+role+" role"}, 201

    @staticmethod
    def login(email, password):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(UserDaoQueries.get_user_by_email(), (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            additional_claims = {"role": user['role']}
            access_token = create_access_token(identity=user['email'], additional_claims=additional_claims)
            return {"access_token": access_token},200
        else:
            return {"message": "Invalid credentials"}, 401
