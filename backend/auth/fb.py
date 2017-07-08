# -*- coding:utf-8 -*-

from flask import g
from flask import request
from flask_restful import Resource
from sqlalchemy.sql import text
import datetime

from backend.util import jwt_required
from backend.util.task import update_state
from backend.errors import success


# POST /auth/fb
class Fb(Resource):
    @jwt_required(scopes=None)
    def post(self, **kwargs):
        u_id, token = kwargs.get('user_id'), request.form.get('token')
        res = {}
        # try:
        query = """
                    INSERT INTO credential (user_id, cred_key, cred_value, expires)
                    VALUES (:id, :key, :token, :expires)
                    ON DUPLICATE KEY UPDATE cred_value=:token, expires=:expires
                """
        expires = datetime.datetime.now() + datetime.timedelta(hours=29)
        g.db.execute(text(query), token=token, id=u_id, key="fb_access_token", expires=expires)

        res['e_msg'] = success()
        update_state(u_id, 1, True, u'토큰 받아오기 완료')

        return res

        # except:
        #    raise Exception
