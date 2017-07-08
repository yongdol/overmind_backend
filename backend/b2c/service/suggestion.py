# -*- coding:utf-8 -*-

from flask import request
from flask import g
from flask_restful import Resource
from sqlalchemy.sql import text

from backend.errors import success


# GET /service/suggestion?service_id={}
class Suggestion(Resource):
    def get(self):
        service_id = request.args.get('service_id')
        res = {}
        try:
            suggested = g.db.execute(text("""SELECT * FROM service WHERE id IN
                                     (SELECT suggested FROM service_suggest
                                     WHERE service_id=:id)"""), id=service_id).fetchall()

            if suggested is None:
                res['e_msg'] = success()
                res['data'] = []
                return res

            suggested = [dict(i.items()) for i in suggested]
            res['data'] = suggested
            res['e_msg'] = success()
            return res

        except:
            raise Exception
