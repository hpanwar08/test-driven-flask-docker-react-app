import json
import unittest

from project.tests.base import BaseTestCase


class TestUserService(BaseTestCase):
    """Test for user service
    """

    def test_users(self):
        """Ensure the /ping route behaves correctly
        """
        response = self.client.get('/users/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_users(self):
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'Iron Man',
                    'email': 'ironman@avengers.com'
                })
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('ironman@avengers.com', data['message'])
            self.assertIn('Success', data['status'])


if __name__ == '__main__':
    unittest.main()
