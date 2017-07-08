from flask import g
from flask_restful import Resource
from sqlalchemy.sql import text

from backend.util import jwt_required
from backend.errors import success, not_found


# GET /auth/me
class Me(Resource):
    @jwt_required(scopes=None)
    def get(self, **kwargs):
        id = kwargs.get('user_id')
        res = {}

        try:
            user_name = g.db.execute(text(""" SELECT customer_user_cred FROM user WHERE id=:id"""), id=id).fetchone()
        except:
            raise Exception

        if user_name is not None:
            res['data'] = dict(name=user_name[0])
            res['e_msg'] = success()
            return res

        res['e_msg'] = not_found('Id not exists')
        return res
