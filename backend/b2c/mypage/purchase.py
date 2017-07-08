# -*- coding:utf-8 -*-

from flask import g
from flask import jsonify
from flask_restful import Resource
from sqlalchemy.sql import text
from backend.util import jwt_required
from backend.errors import success


# GET /mypage/purchase
class Purchase(Resource):
    @jwt_required(scopes=None)
    def get(self, **kwargs):
        res = {}
        user_id = kwargs.get('user_id')

        # job 테이블에서 나의 주문내역 가져오기
        try:
            cursor = g.db
            query = """
                        SELECT j.id, service_id, service_name, try_started_at, try_ended_at, status
                        FROM job as j JOIN service as s ON j.service_id=s.id
                        WHERE user_id=:user_id
                        ORDER BY id DESC
                    """
            rows = cursor.execute(text(query), user_id=user_id).fetchall()

        except:
            raise Exception

        res['e_msg'] = success()
        res['data'] = [dict(i.items()) for i in rows]
        return jsonify(res)
