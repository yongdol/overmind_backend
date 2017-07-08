# -*- coding:utf-8 -*-

from flask import request
from flask import g
from flask import current_app as app
from flask_restful import Resource
from sqlalchemy.sql import text

from werkzeug.security import generate_password_hash
from backend.util import jwt_refresh_token
from backend.errors import success, bad_request


# POST /signup
class SignUp(Resource):
    def post(self):
        name = request.form.get('id')
        pw = request.form.get('pw')
        res = {}

        if len(pw) < 4:
            res['e_msg'] = bad_request('Password too short')
            return res

        try:
            db_id = g.db.execute(text('''SELECT user.id, credential.cred_value
                                         FROM credential JOIN user ON user_id=id
                                         WHERE customer_user_cred=:name AND cred_key=:key '''),
                                 name=name, key="local_pw").fetchone()
        except:
            raise Exception

        if db_id is not None:
            res['e_msg'] = bad_request('User already exists')

        else:
            try:
                g.db.execute(text("INSERT INTO user (customer_user_cred) VALUES (:name)"), name=name)
                index = g.db.execute(text("SELECT id FROM user WHERE customer_user_cred=:name"), name=name).fetchone()[0]

                g.db.execute(text("INSERT INTO credential (user_id, cred_key, cred_value) VALUES (:index, :key, :pw)"),
                             index=index, key='local_pw',
                             pw=generate_password_hash(pw))

                refresh_token = jwt_refresh_token(index, 'master', app.config['SECRET_KEY'])
                g.db.execute(text('''INSERT INTO credential (user_id, cred_key, cred_value)
                                     VALUES (:user_id, :cred_key, :cred_value)'''),
                             user_id=index, cred_key='login_refresh_token', cred_value=refresh_token)

                res['e_msg'] = success()

            except:
                raise Exception

        return res
