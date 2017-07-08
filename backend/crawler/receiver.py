# -*- coding:utf-8 -*-

from flask import g
from flask import request
from flask import jsonify
from datetime import datetime
from flask_restful import Resource
from sqlalchemy.sql import text

import json

from datetime import datetime

from backend.errors import success
from backend.errors import bad_request


# POST /crawler/send-json-report
class Receiver(Resource):
    def post(self, **kwargs):
        print kwargs
        json_report = request.form.get('json_report')

        json_reports = json.loads(json_report)

        # 현재는 크게 의미 없어 주석처리
        # job_info = json_reports['job_info']
        acc_info = json_reports['acc_infos'][0]
        last_crawl = json_reports['last_crawl']

        # For query
        id = acc_info['user']
        crawldate = datetime.now().strftime('%Y-%m-%d')
        data = acc_info['transactions']

        res = {}

        try:
            query = """
            INSERT INTO friskraw(id, crawldate, data, last_crawl)
            VALUES(:id, :crawldate, :data, :last_crawl)
            """
            g.db.execute(text(query), id=str(id), crawldate=crawldate, data=str(data), last_crawl=str(last_crawl))

        except:
            '''
            res['e_msg'] = bad_request("DB ERROR")
            return res
            '''
            raise Exception

        res['e_msg'] = success()
        return res
