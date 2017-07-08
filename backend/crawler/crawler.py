# -*- coding:utf-8 -*-

from flask import g
from flask import request
from flask import jsonify
from datetime import datetime
from flask_restful import Resource
from sqlalchemy.sql import text

from util import make_job_info

from backend.errors import success


# GET /crawler/get-a-job
class Crawler(Resource):
    def get(self, **kwargs):
        res = {}

        try:
            query = """
                SELECT mand.dsource_id, cred.user_id, mand.credcol, cred.cred_value
                FROM (
                    SELECT service_id, sd.dsource_id, credcol
                    FROM service_dsource AS sd
                    JOIN mand_credcol AS mc
                    ON sd.dsource_id = mc.dsource_id
                    WHERE service_id = 80004
                    ) AS mand
                LEFT JOIN (
                    SELECT user_id, cred_key, cred_value
                    FROM credential
                    ) AS cred
                ON mand.credcol = cred.cred_key
                INNER JOIN (
                    SELECT user_id, service_id
                    FROM job
                    WHERE service_id = 80004) AS jb
                ON jb.user_id = cred.user_id
                ORDER BY user_id
                    """

            cred_rows = g.db.execute(text(query)).fetchall()

        except:
            raise Exception

        creds = [dict(i.items()) for i in cred_rows]

        print creds

        creds_sorted = {}

        for row in creds:
            if creds_sorted in (row['user_id']) is not True:
                creds_sorted[row['user_id']] = []
                creds_sorted[row['user_id']].append(row)
            else:
                creds_sorted[row['user_id']].append(row)

        job_infos = []

        for values in creds_sorted.values():
            cred_acc_no = ''
            cred_user_id = ''
            cred_user_pw = ''
            for row in values:
                if row['credcol'] == 'cred_acc_no':
                    cred_acc_no = row['cred_value']
                elif row['credcol'] == 'cred_user_id':
                    cred_user_id = row['cred_value']
                elif row['credcol'] == 'cred_user_pw':
                    cred_user_pw = row['cred_value']
            job_infos.append(
                make_job_info(cred_acc_no=cred_acc_no, cred_user_id=cred_user_id, cred_user_pw=cred_user_pw))

            res['data'] = job_infos
            res['e_msg'] = success()

        return jsonify(res)
