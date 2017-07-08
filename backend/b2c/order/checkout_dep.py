# -*- coding:utf-8 -*-

from flask import g
from flask import request
from flask import jsonify, current_app as app
from datetime import datetime
from flask_restful import Resource
from sqlalchemy.sql import text

from backend.util import jwt_required
from backend.errors import success

# !!WARNING!! THIS IS A DEPRECIATED VIEW
# This is only for Friskweb made with React!


# POST /order/checkout?service_id={}
class CheckoutDeprecated(Resource):
    @jwt_required(scopes=None)
    def get(self, **kwargs):
        res = {}
        service_id = request.args.get('service_id')
        user_id = kwargs.get('user_id')

        # 해당 service에 대한 나의 인증 현황 보여주기
        try:
            query = """
                SELECT mand.dsource_id, mand.credcol, cred.cred_value, cred.expires, mand.redirect
                FROM (
                    SELECT service_id, sd.dsource_id, credcol, redirect
                    FROM service_dsource AS sd
                    JOIN mand_credcol AS mc
                    ON sd.dsource_id = mc.dsource_id
                    WHERE service_id = :service_id
                    ) AS mand
                LEFT JOIN (
                    SELECT user_id, cred_key, cred_value, expires
                    FROM credential
                    WHERE user_id = :user_id
                    ) AS cred
                ON mand.credcol = cred.cred_key
            """
            rows = g.db.execute(text(query), service_id=service_id, user_id=user_id).fetchall()

        except:
            raise Exception

        result = [dict(i.items()) for i in rows]

        # 상황에 따라 status를 다르게 지정
        for row in result:
            row['redirect'] = callback_uri(row['credcol'], user_id, service_id)

            if row['cred_value'] is None:
                row['status'] = 'issue'
            elif row['expires'] is not None and row['expires'] < datetime.utcnow():
                row['status'] = 'renew'
            else:
                row['status'] = 'OK'

        res['data'] = result
        res['e_msg'] = success()

        return jsonify(res)


from config import ProductionConfig as cfg
from backend.util import FriskEncrypt
import urllib
import time
import json
import base64


def callback_uri(credcol, user_id, service_id):

    if credcol == u'fb_access_token':
        enc = FriskEncrypt(app.config['SECRET_KEY'])
        enc_uid = enc.encrypt(str(user_id))

        args = {
            'client_id': cfg.FB_APP_CONFIG['client_id'],
            'redirect_uri': 'https://api.frisk.rocks/auth/fbtemp?' + urllib.urlencode({'u_id': enc_uid, 's_id': service_id}),
            'response_type': 'code',
            'scope': 'user_posts,email'
        }

        return 'https://www.facebook.com/v2.8/dialog/oauth?' + urllib.urlencode(args)

    elif credcol == u'kftc_login_access_token':
        api_url = cfg.KFTC_CONFIG['api_url']
        rd_url = api_url[:api_url.find('v')] + 'oauth/2.0/authorize?'

        crypt = FriskEncrypt(cfg.SECRET_KEY)
        data = {
            'user_id': user_id,
            'service_id': service_id,
            'now': str(int(time.time()))
        }

        client_info = {
            'requester': 'friskweb',
            'data': crypt.encrypt(json.dumps(data))
        }

        args = {
            'scope': 'login',
            'redirect_uri': cfg.REDIRECT_URIS['kftc_login_access_token'],
            'response_type': 'code',
            'client_id': cfg.KFTC_CONFIG['client_id'],
            'client_info': base64.urlsafe_b64encode(json.dumps(client_info))
        }

        return rd_url + urllib.urlencode(args)

    elif credcol == u'kftc_inquiry_access_token':
        api_url = cfg.KFTC_CONFIG['api_url']
        rd_url = api_url[:api_url.find('v')] + 'oauth/2.0/authorize_account?'

        crypt = FriskEncrypt(cfg.SECRET_KEY)
        data = {
            'user_id': user_id,
            'service_id': service_id,
            'now': str(int(time.time()))
        }

        client_info = {
            'requester': 'friskweb',
            'data': crypt.encrypt(json.dumps(data))
        }

        args = {
            'scope': 'inquiry',
            'redirect_uri': cfg.REDIRECT_URIS['kftc_login_access_token'],
            'response_type': 'code',
            'client_id': cfg.KFTC_CONFIG['client_id'],
            'client_info': base64.urlsafe_b64encode(json.dumps(client_info))
        }

        return rd_url + urllib.urlencode(args)

    elif credcol == u'kftc_add_account':
        api_url = cfg.KFTC_CONFIG['api_url']
        rd_url = api_url[:api_url.find('v')] + 'oauth/2.0/register_account?'

        crypt = FriskEncrypt(cfg.SECRET_KEY)
        data = {
            'user_id': user_id,
            'service_id': service_id,
            'now': str(int(time.time()))
        }

        client_info = {
            'requester': 'friskweb',
            'data': crypt.encrypt(json.dumps(data))
        }

        args = {
            'scope': 'inquiry',
            'redirect_uri': cfg.REDIRECT_URIS['kftc_inquiry_access_token'],
            'response_type': 'code',
            'client_id': cfg.KFTC_CONFIG['client_id'],
            'client_info': base64.urlsafe_b64encode(json.dumps(client_info))
        }

        return rd_url + urllib.urlencode(args)

    else:
        return 'http://friskweb-react-gateway.s3-website.ap-northeast-2.amazonaws.com'
