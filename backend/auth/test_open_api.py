import unittest
from flask import json

from backend.app import app
from config import TestingConfig as tcg


class AppTest(unittest.TestCase):
    def setUp(self):
        # self.app = configure_app(app, 'testing')
        self.app = app.test_client()
        self.access_token = self.token()

    def token(self):
        p = self.app.post('/signin', data=dict(
            id=tcg.USERNAME,
            pw=tcg.PASSWORD
        ), follow_redirects=True)

        result = json.loads(p.data)
        self.assertEqual(result['e_msg'].get('status'), 200)

        return result['access_token']

    def test_fb(self):
        pass

    def test_kftc(self):
        pass
