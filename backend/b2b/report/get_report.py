# -*- coding:utf-8 -*-


from flask import request, g
from flask_restful import Resource
from sqlalchemy.sql import text

from backend.util import jwt_required, jwt_token_verify
from backend.errors import success, bad_request, not_found
from backend.b2b.util import member_type_check


# GET /overmind/portco/report
class Report(Resource):
    @jwt_required(scopes=None)
    def get(self, **kwargs):

        user_id = kwargs.get('user_id')
        print "user_id : %s" % user_id
        res = {}

        # member_type check
        member_type = member_type_check(user_id)
        print "member_type : %s" % member_type
        if member_type == 'portco':
            # cursor = g.db.execute(text("SELECT big_json FROM report_json WHERE job_id=1111"))
            cursor = g.db.execute(text("SELECT big_json FROM report_json WHERE job_id=1234"))
            row = cursor.fetchall()

            if len(row) == 0:
                res['e_msg'] = not_found('Data not found')

            else:
                res['e_msg'] = success()
                res['data'] = dict(row.items())

        else:
            res['e_msg'] = bad_request("This Page is only for Portco")

        return res
