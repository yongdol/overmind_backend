# -*- coding:utf-8 -*-

from flask import g
from flask import request
from flask_restful import Resource
from sqlalchemy.sql import text
from backend.errors import success, bad_request


# POST /overmind/addpf/
class AddPf(Resource):
    def post(self):
        name = request.args.get('name')
        remain_month = request.args.get('drmonth')
        monthly_use = request.args.get('dmum')
        remain_money = request.args.get('drmoney')

        res = {}
        try:
            sql = "INSERT INTO portfolios (name, remain_month, monthly_use_money, remain_money) VALUES (%s, %s, %s, %s)"
            g.db.execute(sql, (name, remain_month, monthly_use, remain_money))

            confirm_sql = "SELECT * FROM portfolios WHERE name=:name"
            confirm_res = g.db.execute(text(confirm_sql), name=name).fetchall()
            sql_res = [dict(i.items()) for i in confirm_res]
            res['data'] = sql_res
            res['e_msg'] = success()

        except:
            raise Exception

        return res

