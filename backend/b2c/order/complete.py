# -*- coding:utf-8 -*-

from flask import g
from flask import request
from flask_restful import Resource
from sqlalchemy.sql import text

from backend.util import jwt_required
from backend.util.task import validate_all, required_tasks
from backend.errors import success, bad_request


# POST /order/completed
class Complete(Resource):
    @jwt_required(scopes=None)
    def post(self, **kwarg):
        service_req = request.form.get('service_id')
        user_req = kwarg.get('user_id')
        res = {}

        # service id가 유효한지 확인
        if not g.db.execute(text('SELECT id FROM service WHERE id = :id'), id=service_req).fetchone():
            res['e_msg'] = bad_request('Service id invalid')
            return res

        if False in validate_all(user_id=user_req, task_ids=required_tasks(service_req)).values():
            res['e_msg'] = bad_request('Not all requited tasks are done. Please check again.')
            return res

        data = {
            'service_id': service_req,
            'user_id': user_req,
            'status': 'waiting'
        }

        try:
            # job table 업데이트
            query = text("""
            INSERT INTO job (user_id,service_id,status)
            VALUES (:user_id,:service_id,:status)
            """)
            cursor = g.db.execute(query, **data)
            id = str(cursor.lastrowid)

            # job_log table 업데이트
            query = text("""
            INSERT INTO job_log (step_id, job_id, step_co_name)
            VALUES (:step_id,:job_id,:step_co_name)""")
            g.db.execute(query, step_id=1, job_id=id, step_co_name='preparing')

            # 방금 업데이트 한 내역 불러오기
            row = g.db.execute(text("""SELECT id,user_id,service_id FROM job WHERE id=:id"""), id=id).fetchone()

        except:
            raise Exception

        res['e_msg'] = success()
        res['data'] = dict(row.items())

        return res
