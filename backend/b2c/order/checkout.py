# -*- coding:utf-8 -*-

from flask import request
from flask import jsonify
from flask_restful import Resource

from backend.util import jwt_required
from backend.util.task import check_service
from backend.errors import success


# POST /order/checkout?service_id={}
class Checkout(Resource):
    @jwt_required(scopes=None)
    def get(self, **kwargs):
        service_id = request.args.get('service_id')
        user_id = kwargs.get('user_id')

        result = check_service(user_id, service_id)

        res = {
            'e_msg': success(),
            'data': result.values()
        }

        return jsonify(res)
