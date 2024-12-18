from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id: int, login: str, password: str):
        self.id = id
        self.login = login
        self.password = password
