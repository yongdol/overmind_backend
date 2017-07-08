# -*- coding:utf-8 -*-

from flask import g
from flask import request
from flask_restful import Resource
from sqlalchemy.sql import text

from backend.errors import success, bad_request
from backend.util import jwt_required

# GET /overmind/pflist/pf?pf_id={}
class Pf(Resource):
    @jwt_required(scopes=None)
    def get(self, **kwargs):
        res = {}
        pf_id = request.args.get('pf_id')
        job_id = request.args.get('job_id')


        try:
            info = g.db.execute(text("SELECT * FROM portfolios WHERE id=:id"), id=pf_id).fetchall()

        except:
            raise Exception

        if info is None or len(info) <= 0:
            res['e_msg'] = bad_request('Portfolio id not found')

        info = [dict(i.items()) for i in info]
        res['data'] = info[0]
        res['e_msg'] = success()

        return res
