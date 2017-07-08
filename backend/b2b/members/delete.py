# -*- coding:utf-8 -*-

from flask import request
from flask import g
from flask_restful import Resource
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash

from backend.util import jwt_required
from backend.errors import success, bad_request


# POST /delete?pw={}
class Delete(Resource):
    @jwt_required(scopes=None)
    def post(self, **kwargs):
        res = {}

        u_id = kwargs.get('user_id')
        pw = request.form.get('pw')
        try:
            query = "SELECT cred_value FROM credential " \
                    "WHERE user_id=:u_id AND cred_key = 'local_pw'"
            result = g.db.execute(text(query), u_id=u_id).fetchone()

            if result is None:
                res['e_msg'] = bad_request('User invalid')
            db_pw = result[0]

            if not check_password_hash(db_pw, pw):
                res['e_msg'] = bad_request('User invalid')

            g.db.execute(text("""DELETE FROM user WHERE id=:id"""), id=u_id)
            g.db.execute(text("""DELETE FROM credential WHERE user_id=:id"""), id=u_id)
            res['e_msg'] = success()

        except:
            raise Exception

        return res
