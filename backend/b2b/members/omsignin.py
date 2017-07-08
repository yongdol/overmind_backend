# -*- coding:utf-8 -*-

from flask import request
from flask import g
from flask import current_app as app
from flask_restful import Resource
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash

from backend.util import jwt_access_token, jwt_scope_verify
from backend.errors import success, not_found, unauthorized, bad_request


# POST /overmind/signin
class OMSignIn(Resource):
    def post(self):
        name = request.form.get('id')
        pw = request.form.get('pw')
        # name = request.args.get('id')
        # pw = request.args.get('pw')
        res = {}

        try:
            db_info = g.db.execute(text('''SELECT user.id, credential.cred_value
                                   FROM credential JOIN user ON user_id=id
                                   WHERE customer_user_cred=:name AND cred_key=:key'''),
                                   name=name, key="local_pw").fetchone()
        except:
            raise Exception

        if db_info is None:
            res['e_msg'] = bad_request('User not found')

        else:
            db_user_id = db_info[0]
            db_pw = db_info[1]

            # member type
            mem_type_query = 'SELECT member_type FROM user JOIN firm_info ON firm_info.firm_id=user.firm_id \
                       where user.customer_user_cred=:name'
            mem_type = g.db.execute(text(mem_type_query), name=name).fetchone()[0]
            res['member_type'] = mem_type


            # If user matched, get refresh token
            if check_password_hash(db_pw, pw):
                query = "SELECT cred_value FROM credential WHERE cred_key='login_refresh_token' AND user_id=:id"
                refresh_token = g.db.execute(text(query), id=db_user_id).fetchone()[0]
                res['refresh_token'] = refresh_token

                # If scope verified, get access token
                if jwt_scope_verify(str(refresh_token), app.config['SECRET_KEY']):
                    access_token = jwt_access_token(db_user_id, 31536000, app.config['SECRET_KEY'], 'master')
                    res['access_token'] = access_token

                res['e_msg'] = success()

            else:
                res['e_msg'] = unauthorized('User id or password invalid, please try again')
        return res
