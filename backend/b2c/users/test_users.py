from flask import json
import unittest

from config import TestingConfig as tcg
from backend.app import app


class AppTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.access_token = self.token()

    def token(self, username=tcg.USERNAME, password=tcg.PASSWORD):
        p = self.app.post('/signin', data=dict(
            id=username,
            pw=password
        ), follow_redirects=True)

        result = json.loads(p.data)
        self.assertEqual(result['e_msg'].get('status'), 200)

        return result['access_token']

    def test_signin(self):
        # Invalid Username
        p = self.app.post('/signin', data=dict(
            id=tcg.USERNAME + 'xxx',
            pw=tcg.PASSWORD
        ))
        result = json.loads(p.data)
        self.assertEqual(result['e_msg'].get('message'), 'User not found')

        # Invalid Password
        p = self.app.post('/signin', data=dict(
            id=tcg.USERNAME,
            pw=tcg.PASSWORD + 'x'
        ))
        result = json.loads(p.data)
        self.assertEqual(result['e_msg'].get('message'), 'User id or password invalid, please try again')

    def test_signup(self):
        p = self.app.post('/signup', data=dict(
            id=tcg.USERNAME,
            pw=tcg.PASSWORD
        ))
        result = json.loads(p.data)
        self.assertEqual(result['e_msg'].get('message'), 'User already exists')

        # p = self.app.post('/signup', data=dict(
        #     id=tcg.USERNAME + 'x',
        #     pw=tcg.PASSWORD
        # ))
        # result = json.loads(p.data)
        # self.assertEqual(result['e_msg'].get('status'), 200)

    def test_delete(self):
        # TODO: Delete exception
        # p = self.app.post('/delete', data=dict(
        #     id=tcg.USERNAME + 'x',
        #     pw=tcg.PASSWORD
        # ))
        # result = json.loads(p.data)
        # self.assertEqual(result['message'], 'Internal Server Error')

        # TODO: Delete user
        # p = self.app.post('/delete', data=dict(
        #     headers={'Authorization': 'JWT {}'.format(self.access_token)},
        #     query_string={'pw': tcg.PASSWORD}
        # ))
        # result = json.loads(p.data)
        # self.assertEqual(result['e_msg'].get('status'), 200)
        pass

    def test_update(self):
        # TODO: Update user
        pass
