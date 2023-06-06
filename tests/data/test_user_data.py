import random
import string
from datetime import date


class UserTestData:
    @property
    def existing_user(self):
        return {
            "id": "49266b33-1a3b-424b-b436-252e8054ecfc",
            "first_name": "first_name",
            "last_name": "last_name",
            "username": "username",
            "email": "test@example.com",
            "phone": "0500000000",
            "hash_password": "1234",
            "birth_date": date.today(),
            "national_id": random.choices(string.hexdigits),
            "id_expiration": date.today(),
        }

    @property
    def create_user(self):
        return {
            "first_name": "first_name",
            "last_name": "last_name",
            "username": "new username",
            "email": "new@example.com",
            "phone": "0200000000",
            "password": "0000",
            "birth_date": str(date.today()),
            "national_id": str(random.choices(string.digits)),
            "id_expiration": str(date.today()),
        }

    @property
    def update_user(self):
        return {"email": "update@example.com"}

    @property
    def login_user(self):
        return {
            "username": self.existing_user.get("username"),
            "password": self.existing_user.get("hash_password"),
        }

    @property
    def existing_otp(self):
        return {"user_id": self.existing_user.get("id")}
