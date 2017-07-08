# -*-coding:utf-8-*-

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

    def test_purchase(self):
        g = self.app.get('/mypage/purchase', headers={'Authorization': 'JWT {}'.format(self.access_token)})
        result = json.loads(g.data)
        self.assertEqual(result['e_msg'].get('status'), 200)
        self.assertGreater(len(result['data']), 0)

    def test_purchase_status(self):
        g = self.app.get('/mypage/purchase/status',
                         headers={'Authorization': 'JWT {}'.format(self.access_token)},
                         query_string={'order_id': 734})
        result = json.loads(g.data)
        self.assertEqual(result['e_msg'].get('status'), 200)
        self.assertGreater(len(result['data']), 0)

    def test_report(self):
        g = self.app.get('/mypage/purchase/report',
                         headers={'Authorization': 'JWT {}'.format(self.access_token)},
                         query_string={'job_id': 734})
        result = json.loads(g.data)
        self.assertEqual(result['e_msg'].get('status'), 200)
