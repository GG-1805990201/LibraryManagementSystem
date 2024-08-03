from flask import url_for
from config.sqlite_config import get_db_connection
from dao.member_dao_queries import MemberDaoQueries


class MemberService:
    @staticmethod
    def get_members():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(MemberDaoQueries.get_all_members())
        members = cursor.fetchall()
        conn.close()
        return [dict(member) for member in members]

    @staticmethod
    def get_member_by_id(member_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(MemberDaoQueries.get_member_by_id(), (member_id,))
        member = cursor.fetchone()
        conn.close()
        return dict(member) if member else None

    @staticmethod
    def update_member(member_id, data):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(MemberDaoQueries.update_member(), (data['name'], data['email'], data['join_date'], member_id))
        conn.commit()
        conn.close()
        return {"message": "Member updated successfully"}

    @staticmethod
    def delete_member(member_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(MemberDaoQueries.delete_member_by_id(), (member_id,))
        conn.commit()
        conn.close()
        return {"message": "Member deleted successfully"}
