# -*- coding:utf-8 -*-

from flask_restful import Resource
from flask import request, g, redirect
from flask import current_app as app
from sqlalchemy import text

from backend.util import FriskEncrypt
from backend.util.task import update_state
from backend.errors import success

import datetime
import requests
import urllib


# Temporary Endpoint for Friskweb React ONLY!
class FbTemp(Resource):
    def get(self):
        enc = FriskEncrypt(app.config['SECRET_KEY'])
        u_id, s_id, code = request.args.get('u_id'), request.args.get('s_id'), request.args.get('code')

        fb_result = requests.get('https://graph.facebook.com/v2.8/oauth/access_token', params={
            'client_id': app.config['FB_APP_CONFIG']['client_id'],
            'redirect_uri': 'https://api.frisk.rocks/auth/fbtemp?' + urllib.urlencode({'u_id': u_id, 's_id': s_id}),
            'client_secret': app.config['FB_APP_CONFIG']['app_secret'],
            'code': code
        }).json()

        dec_uid = enc.decrypt(urllib.unquote(u_id).encode('utf-8'))

        # try:
        query = """
                    INSERT INTO credential (user_id, cred_key, cred_value, expires)
                    VALUES (:id, :key, :token, :expires)
                    ON DUPLICATE KEY UPDATE cred_value=:token, expires=:expires
                """
        expires = datetime.datetime.now() + datetime.timedelta(hours=29)
        g.db.execute(text(query), token=fb_result['access_token'], id=dec_uid, key="fb_access_token", expires=expires)

        res = dict()

        res['e_msg'] = success()
        update_state(u_id, 1, True, u'토큰 받아오기 완료')

        uri_to_go = 'http://friskweb-react-gateway.s3-website.ap-northeast-2.amazonaws.com/#/service/{}/purchase/1' \
            .format(s_id)

        return redirect(uri_to_go)
