class User:
    def __init__(self):
        self.id = None
        self.username = None
        self.password = None
        self.email = None
        self.active = None

    def get_mapping(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "active": self.active
        }
