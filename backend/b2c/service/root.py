# -*- coding:utf-8 -*-

from flask import g
from sqlalchemy.sql import text
from flask_restful import Resource

from backend.errors import success, not_found


# GET /service
class Root(Resource):
    def get(self):
        res = {}

        try:
            res['data'] = g.db.execute(text("SELECT * FROM service")).fetchall()
        except:
            raise Exception

        if res is None or len(res['data']) <= 0:
            res['e_msg'] = not_found('Service id not found')
            return res

        res['data'] = [dict(i.items()) for i in res['data']]
        res['e_msg'] = success()

        return res
