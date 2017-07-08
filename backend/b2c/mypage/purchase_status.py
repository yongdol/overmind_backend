# -*- coding:utf-8 -*-

from flask import g
from flask import request
from flask_restful import Resource
from sqlalchemy.sql import text

from backend.util import jwt_required
from backend.errors import success, bad_request


# GET /mypage/purchase/status?order_id={}
class PurchaseStatus(Resource):
    @jwt_required(scopes=None)
    def get(self, **kwargs):

        # TODO: order_id and job_id need convention unity

        order_id = request.args.get('order_id')
        user_id = kwargs.get('user_id')
        res = {}

        # user_id 와 order_id가 매칭되는지 확인
        try:
            query = text("""SELECT user_id FROM job WHERE id=:id""")
            cursor = g.db.execute(query, id=order_id)
            row = dict(cursor.fetchone().items())

            if not int(row['user_id']) is int(user_id):
                res['e_msg'] = bad_request('User, order id mismatched')

            # 매칭되면 job_log 테이블에서 데이터 가져오기
            query = text("""SELECT job_id,step_id,step_co_name,step_class_name,e_msg,tb_msg
                            FROM job_log WHERE job_log.job_id=:order_id""")
            rows = g.db.execute(query, order_id=order_id).fetchall()

        except:
            raise Exception

        res['e_msg'] = success()
        res['data'] = [dict(i.items()) for i in rows]
        return res
