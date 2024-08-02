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

        # Add HATEOAS links to each member
        members_with_links = []
        for member in members:
            member_dict = dict(member)
            member_dict["_links"] = {
                "self": url_for('members.get_member_by_id', member_id=member['id'], _external=True),
                "update": url_for('members.update_member', member_id=member['id'], _external=True),
                "delete": url_for('members.delete_member', member_id=member['id'], _external=True)
            }
            members_with_links.append(member_dict)

        # Add a link to create a new member
        links = {"create": url_for('members.create_member', _external=True)}

        return {"members": members_with_links, "_links": links}

    @staticmethod
    def get_member_by_id(member_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(MemberDaoQueries.get_member_by_id(), (member_id,))
        member = cursor.fetchone()
        conn.close()

        if member:
            # Add HATEOAS links
            member_dict = dict(member)
            member_dict["_links"] = {
                "self": url_for('members.get_member_by_id', member_id=member_id, _external=True),
                "update": url_for('members.update_member', member_id=member_id, _external=True),
                "delete": url_for('members.delete_member', member_id=member_id, _external=True),
                "list": url_for('members.get_members', _external=True)
            }
            return member_dict
        else:
            return None

    @staticmethod
    def update_member(member_id, data):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(MemberDaoQueries.update_member(), (data['name'], data['email'], data['join_date'], member_id))
        conn.commit()
        conn.close()

        # Add HATEOAS links
        response = {
            "message": "Member updated successfully",
            "_links": {
                "self": url_for('members.get_member_by_id', member_id=member_id, _external=True),
                "delete": url_for('members.delete_member', member_id=member_id, _external=True),
                "list": url_for('members.get_members', _external=True)
            }
        }
        return response

    @staticmethod
    def delete_member(member_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(MemberDaoQueries.delete_member_by_id(), (member_id,))
        conn.commit()
        conn.close()

        # Add HATEOAS link to list members
        response = {
            "message": "Member deleted successfully",
            "_links": {
                "list": url_for('members.get_members', _external=True)
            }
        }
        return response
