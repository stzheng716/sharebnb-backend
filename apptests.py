import os

os.environ["DATABASE_URL"] = 'postgresql:///sharebnb_test'

from unittest import TestCase

from app import app
from models import db, User

app.config['TESTING'] = True

db.drop_all()
db.create_all()

USER_DATA_SQL = {     
    "username":"testuser1",
    "first_name":"firsttest",
    "last_name":"lasttest",
    "email":"email@gmail.com",
    "password":"$2b$12$LURcsX0Icw4/37Job1WjNO/rIkP.Do3vfCtIaA7gytqrn5B5y.Dua",
    "is_host":False
}

USER_DATA_JSON = {     
    "username":"testuser2",
    "firstName":"firsttest",
    "lastName":"lasttest",
    "email":"email2@gmail.com",
    "password":"$2b$12$LURcsX0Icw4/37Job1WjNO/rIkP.Do3vfCtIaA7gytqrn5B5y.Dua",
    "isHost":False
}

class UserViewsTestCase(TestCase):
    """Tests for views of API."""

    def setUp(self):
        """Make demo data."""

        User.query.delete()

        # "**" means "pass this dictionary as individual named params"
        user = User(**USER_DATA_SQL)
        db.session.add(user)
        db.session.commit()

        self.user_username = user.username

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_get_user(self):
        """test to get an existing user in the database"""

        with app.test_client() as client:
            url = f"/users/{self.user_username}"
            resp = client.get(url)

        self.assertEqual(resp.status_code, 200)
        data = resp.json

        self.assertEqual(data, {
                "user": {
                    "username": "testuser1",
                    "first_name":"firsttest",
                    "last_name":"lasttest",
                    "email":"email@gmail.com",
                    "is_host":False,
                    'bookings': [],
                    'listings': [],
                    'sent_messages': []
                }
            })
    
    def test_get_nonexisting_user(self):
        with app.test_client() as client:
            url = f"/users/user_not_in_data_base"
            resp = client.get(url)

        self.assertEqual(resp.status_code, 404)
        data = resp.json
        
        self.assertEqual(data, {
                "error": {
                    "message":"No user: user_not_in_data_base"
                }
            })
        
    def test_new_user_signup(self):
            """test to get an JWT from the auth/signup route"""

            with app.test_client() as client:
                url = f"/auth/signup"
                resp = client.post(url, json=USER_DATA_JSON)

            self.assertEqual(resp.status_code, 201)
            data = resp.json

            self.assertIsInstance(data["token"], str)
    
    def test_existing_username_signup(self):
            """test sign up of user with existing username"""

            with app.test_client() as client:
                url = f"/auth/signup"
                resp = client.post(url, json=USER_DATA_JSON)

            self.assertEqual(resp.status_code, 409)
            data = resp.json

            self.assertEqual(data, {"error":{"message": "Username already exists"}})