# -*- coding:utf-8 -*-

from flask_restful import Resource
from flask import request, g
from werkzeug.security import generate_password_hash

from sqlalchemy import text
from backend.util import jwt_required
from backend.errors import success, not_found


# POST /update
class Update(Resource):
    @jwt_required(scopes=None)
    def post(self, **kwargs):
        attr = request.form.get('attribute')
        to = request.form.get('to')
        u_id = kwargs.get('user_id')
        res = dict()

        try:
            if attr == 'pw':
                query = "INSERT INTO credential (user_id, cred_key, cred_value) " \
                        "VALUES (:user_id, :cred_key, :cred_value) " \
                        "ON DUPLICATE KEY UPDATE cred_key=:cred_key, cred_value=:cred_value;"
                g.db.execute(text(query), user_id=u_id, cred_key='local_pw', cred_value=generate_password_hash(to))
                res['e_msg'] = success()
            else:
                res['e_msg'] = not_found('User not found')
        except:
            raise Exception

        return res
