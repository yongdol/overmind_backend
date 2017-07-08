# -*- coding:utf-8 -*-

from flask import g
from flask_restful import Resource
from sqlalchemy.sql import text

from backend.errors import success


# GET /auth/list
class Auth(Resource):
    def get(self):
        res = {}

        # 전체 인증 기업 리스트 불러오기
        try:
            cursor = g.db
            rows = cursor.execute(text("""SELECT id, disp_name, acc_type FROM dsource""")).fetchall()
        except:
            raise Exception

        res['data'] = [dict(i.items()) for i in rows]
        res['e_msg'] = success()
        return res
