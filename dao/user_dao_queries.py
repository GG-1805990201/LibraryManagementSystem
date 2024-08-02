class UserDaoQueries:

    @staticmethod
    def get_user_by_member_id():
        return 'SELECT * FROM Users WHERE member_id = ?'

    @staticmethod
    def get_user_by_email():
        return 'SELECT * FROM Users WHERE email = ?'

    @staticmethod
    def insert_new_user():
        return 'INSERT INTO Users (member_id, email, password_hash, role) VALUES (?, ?, ?, ?)'



