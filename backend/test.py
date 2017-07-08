# -*-coding:utf-8-*-

import pytest
from flask import json

from backend.app import app
from config import TestingConfig as tcg


@pytest.fixture(scope='session')
def client():
    client = app.test_client()
    return client


@pytest.fixture(scope='session')
def access_token(client):
    p = client.post('/signin', data=dict(
        username=tcg.USERNAME,
        password=tcg.PASSWORD
    ))
    result = json.loads(p.data)
    return result['access_token']


def test_login(client):
    p = client.post('/signin', data=dict(
        username=tcg.USERNAME,
        password=tcg.PASSWORD
    ))
    result = json.loads(p.data)
    assert result['e_msg'].get('message') == 'User not found'
