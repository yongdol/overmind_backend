# -*- coding:utf-8 -*-

import datetime

from flask import g
from flask import request, redirect
from flask_restful import Resource
from flask import current_app as app
from sqlalchemy.sql import text

from backend.util import FriskEncrypt
from backend.util.KFTCAPI import KFTCAuth
from backend.util.task import update_state
from backend.errors import success, bad_request

import json
import base64
import time
import urlparse


# GET /auth/kftc
class Kftc(Resource):
    def get(self):
        code = request.args.get('code')
        scope = request.args.get('scope')
        try:
            referer = request.headers['referer']
            parsed_url = urlparse.urlparse(referer)
            parsed_query = urlparse.parse_qs(parsed_url.query)
        except KeyError:
            parsed_query = {}

        if 'client_info' in parsed_query:
            client_info = json.loads(base64.urlsafe_b64decode(str(parsed_query['client_info'][0])))
        else:
            client_info = json.loads(base64.urlsafe_b64decode(str(request.args.get('client_info'))))

        requester = client_info['requester']

        if requester == 'friskweb':
            data = json.loads(FriskEncrypt(app.config['SECRET_KEY']).decrypt(client_info['data']))
            u_id = data['user_id']
            redirect_uri = 'http://friskweb-react-gateway.s3-website.ap-northeast-2.amazonaws.com/#/service/{}/purchase/1'.format(
                data['service_id']
            )
            now = data['now']
        elif requester == 'friskweb_t':
            data = json.loads(FriskEncrypt(app.config['SECRET_KEY']).decrypt(client_info['data']))
            u_id = data['user_id']
            redirect_uri = 'http://www.frisk.rocks:5505/order/?service_id={}'.format(
                data['service_id']
            )
            now = data['now']

        elif requester == 'test':
            data = json.loads(FriskEncrypt(app.config['SECRET_KEY']).decrypt(client_info['data']))
            u_id = data['user_id']
            now = data['now']

        else:
            return {'e_msg': bad_request('Cannot verify the request')}

        # 정보 기한 만료 시 바로 리다이렉트
        if int(now) + 60 < time.time():
            return redirect(redirect_uri)

        try:
            # KFTC로 code를 보내고 token관련 정보를 얻어옴
            result = KFTCAuth().get_token(code)

            # 응답을 바탕으로 필요한 정보 얻기
            access_token = result['access_token']
            expires = datetime.datetime.now() + datetime.timedelta(seconds=result['expires_in'])
            refresh_token = result['refresh_token']
            user_seq_no = result['user_seq_no']
            cred_key = {
                'login': 'kftc_login_access_token',
                'inquiry': 'kftc_inquiry_access_token'
            }.get(result['scope'])
            cred_key_refresh = {
                'login': 'kftc_login_refresh_token',
                'inquiry': 'kftc_inquiry_refresh_token'
            }.get(result['scope'])

            res = {}

            # access_token DB에 씀
            query = "INSERT INTO credential (user_id, cred_key, cred_value, expires) " \
                    "VALUES (:id, :cred_key, :cred_value, :expires) " \
                    "ON DUPLICATE KEY UPDATE cred_value=:cred_value, expires=:expires;"
            g.db.execute(text(query), id=u_id, cred_key=cred_key, cred_value=access_token, expires=expires)

            # refresh_token DB에 씀
            query = "INSERT INTO credential (user_id, cred_key, cred_value) " \
                    "VALUES (:id, :cred_key, :cred_value) " \
                    "ON DUPLICATE KEY UPDATE cred_value=:cred_value;"
            g.db.execute(text(query), id=u_id, cred_key=cred_key_refresh, cred_value=refresh_token, expires=expires)

            # user_seq_no(KFTC에서 user를 구분하는 id) DB에 씀
            query = "INSERT INTO credential (user_id, cred_key, cred_value) " \
                    "VALUES (:u_id, :cred_key, :cred_value) " \
                    "ON DUPLICATE KEY UPDATE cred_value=:cred_value"
            g.db.execute(text(query), u_id=u_id, cred_key='kftc_user_seq_no', cred_value=user_seq_no)

            res['e_msg'] = success()

            if result.get('scope') == u'login':
                update_state(u_id, 2, True, u'토큰 받아오기 완료')
            elif result.get('scope') == u'inquiry':
                update_state(u_id, 3, True, u'토큰 받아오기 완료')

        except:
            raise Exception

        if requester == 'test':
            return 'Access Token: {}'.format(access_token)
        else:
            return redirect(redirect_uri)
