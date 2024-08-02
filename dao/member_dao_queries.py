class MemberDaoQueries:
    @staticmethod
    def get_all_members():
        return "SELECT * FROM Member"

    @staticmethod
    def get_member_by_id():
        return "SELECT * FROM Members WHERE id = ?"

    @staticmethod
    def insert_new_member():
        return "INSERT INTO Members (name, email, join_date) VALUES (?, ?, ?)"

    @staticmethod
    def update_member():
        return "UPDATE Members SET name = ?, email = ?, join_date = ? WHERE id = ?"

    @staticmethod
    def delete_member_by_id():
        return "DELETE FROM Members WHERE id = ?"
