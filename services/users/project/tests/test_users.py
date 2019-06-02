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

    def test_single_user(self):
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

    def test_single_user_no_id(self):
        """Ensure correct message is returned when no userid
        """
        with self.client:
            response = self.client.get(f'/user/abc')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exists', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user_invalid_id(self):
        """Ensure correct message is returned when invalid userid
        """
        with self.client:
            response = self.client.get(f'/user/999999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exists', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_users(self):
        """Ensure all users are returned
        """
        add_user('Captian American', 'cptamerica@avenger.com')
        add_user('Ant Man', 'antman@avenger.com')

        with self.client:
            response = self.client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('Captian American', data['users'][0]['username'])
            self.assertIn('cptamerica@avenger.com', data['users'][0]['email'])
            self.assertIn('Ant Man', data['users'][1]['username'])
            self.assertIn('antman@avenger.com', data['users'][1]['email'])
            self.assertIn('success', data['status'])

    def test_main_no_users(self):
        """Ensure correct html is displayed when no users
        """
        with self.client:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertIn(b'<p>No users!</p>', response.data)

    def test_main_with_users(self):
        """Ensure correct html is displayed when there are users
        """
        add_user(username='Captian American', email='cptamerica@avenger.com')
        add_user(username='Ant Man', email='antman@avenger.com')
        with self.client:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'<p>No users!</p>', response.data)
            self.assertIn(b'Captian American', response.data)
            self.assertIn(b'Ant Man', response.data)

    def test_main_add_user(self):
        with self.client:
            response = self.client.post(
                '/',
                data=dict(username='Iron Man', email='ironman@avengers.com'),
                follow_redirects=True
                )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'<p>No users!</p>', response.data)
            self.assertIn(b'Iron Man', response.data)


if __name__ == '__main__':
    unittest.main()
