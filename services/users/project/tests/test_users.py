import json
import unittest

from project.tests.base import BaseTestCase
from project.api.models import User
from project import db


def add_user(username, email):
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return user


class TestUserService(BaseTestCase):
    """Test for user service
    """

    def test_users_ping(self):
        """Ensure the /ping route behaves correctly
        """
        response = self.client.get('/users/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user(self):
        """Ensure single user is added
        """
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'Iron Man',
                    'email': 'ironman@avengers.com'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('ironman@avengers.com was added', data['message'])
            self.assertIn('Success', data['status'])

    def test_users_invalid_json(self):
        """Ensure correct message is returned when invalid json is sent
        """
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid json', data['message'])
            self.assertIn('fail', data['status'])

    def test_users_invalid_json_keys(self):
        """Ensure correct message is returned when invalid json key is sent
        """
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'email': 'ironman@avengers.com'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid json', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_duplicate(self):
        """Ensure that duplicate user is not added
        """
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'Iron Man',
                    'email': 'ironman@avengers.com'
                }),
                content_type='application/json'
            )

            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'Iron Man',
                    'email': 'ironman@avengers.com'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'Sorry. ironman@avengers.com already exists',
                data['message'])
            self.assertIn('fail', data['status'])

    def test_get_single_user(self):
        """Ensure a single user is returned by id
        """
        user = add_user('Dr. Strange', 'drstrange@avenger.com')
        with self.client:
            response = self.client.get(f'/user/{user.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('Dr. Strange', data['data']['username'])
            self.assertIn('drstrange@avenger.com', data['data']['email'])
            self.assertIn('success', data['status'])


if __name__ == '__main__':
    unittest.main()
