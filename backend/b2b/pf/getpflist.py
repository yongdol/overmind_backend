# -*- coding:utf-8 -*-

from flask import g, jsonify, request
from flask_restful import Resource
from sqlalchemy.sql import text

from backend.b2b.util import member_type_check
from backend.util import jwt_required
from backend.errors import success, not_found, bad_request
import json


# GET /overmind/vc/pflist
class Pflist(Resource):
    @jwt_required(scopes=None)
    def get(self, **kwargs):
        res = {}
        user_id = kwargs.get('user_id')

        print "user_id : %s" % user_id

        member_type = member_type_check(user_id)
        if member_type == 'vc':
            query = text("SELECT firm_name, status, runway, avg_burn_mon, cash_remaining \
                        FROM overview inner join firm_info on overview.firm_id = firm_info.firm_id")
            res['data'] = g.db.execute(query).fetchall()

            if res is None or len(res['data']) <= 0:
                res['e_msg'] = not_found('Portfolio is not found')
                return res

            else:
                res['data'] = [dict(i.items()) for i in res['data']]
                res['e_msg'] = success()

        else:
            res['e_msg'] = bad_request('This page is only for VC')

        return res
