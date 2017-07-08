# -*- coding:utf-8 -*-

from flask import g
from flask import request
from flask_restful import Resource
from sqlalchemy.sql import text

from backend.errors import success, bad_request


# GET /service/detail?service_id={}
class Detail(Resource):
    def get(self):
        res = {}
        service_id = request.args.get('service_id')

        try:
            info = g.db.execute(text("SELECT * FROM service WHERE id=:id"), id=service_id).fetchall()

        except:
            raise Exception

        if info is None or len(info) <= 0:
            res['e_msg'] = bad_request('Service id not found')

        info = [dict(i.items()) for i in info]
        res['data'] = info[0]
        res['e_msg'] = success()

        return res
