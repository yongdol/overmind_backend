# -*- coding:utf-8 -*-

from flask import g
from flask import request
from flask_restful import Resource
from sqlalchemy.sql import text

from backend.util import jwt_required
from backend.errors import success, bad_request, not_found


# GET /mypage/purchase/report?order_id={}
class Report(Resource):
    @jwt_required(scopes=None)
    def get(self, **kwargs):

        # TODO: order_id should be changed to 'report_id'
        # TODO: report template for EAV table should be made

        job_id = request.args.get('job_id')
        user_id = kwargs.get('user_id')
        res = {}

        # user_id와 order_id(report_id)가 매칭되는지 비교
        try:
            query = text("SELECT user_id FROM job WHERE id=:job_id")
            cursor = g.db.execute(query, job_id=job_id)
            row = dict(cursor.fetchone().items())

            if not int(row['user_id']) is int(user_id):
                res['e_msg'] = bad_request('User, order id mismatched')

            # 매칭되면 report 데이터 불러오기
            cursor = g.db.execute(text("SELECT big_json FROM report_json WHERE job_id=:job_id"), job_id=job_id)
            row = cursor.fetchone()

            if len(row) == 0:
                res['e_msg'] = not_found('Data not found')

        except:
            raise Exception

        res['e_msg'] = success()
        res['data'] = dict(row.items())
        return res
