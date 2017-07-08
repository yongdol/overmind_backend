# -*- coding:utf-8 -*-

from flask import g
from flask import request
from flask_restful import Resource
from sqlalchemy.sql import text

from backend.util import jwt_required
from backend.errors import success


# GET /auth/status
class AuthStatus(Resource):
    @jwt_required(scopes=None)
    def get(self, **kwargs):
        res = {}
        dsource_id = request.args.get('dsource_id')
        user_id = kwargs.get('user_id')

        # 해당 기업에 대해 나의 인증 현황 불러오기
        try:
            cursor = g.db
            query = text("""
                    SELECT credential.user_id, mand.id, mand.disp_name, mand.acc_type,
                    mand.credcol, mand.redirect, credential.cred_value, credential.expires,
                    if(credential.cred_value is null,'issue',if(credential.expires>now(),'OK','renew')) as status
                    FROM
                    (SELECT dsource.id, dsource.disp_name, dsource.acc_type, mand_credcol.credcol, mand_credcol.redirect
                     FROM dsource
                     JOIN mand_credcol
                     ON dsource.id=mand_credcol.dsource_id) as mand
                    LEFT JOIN
                    (SELECT *
                     FROM credential
                     WHERE user_id=:user_id) as credential
                    ON
                    mand.credcol=credential.cred_key
                    WHERE
                    mand.id=:dsource_id
                    """)
            rows = cursor.execute(query, user_id=user_id, dsource_id=dsource_id).fetchall()
            res['data'] = [dict(i.items()) for i in rows]

            for datum in res['data']:
                datum['expires'] = str(datum['expires'])
            res['e_msg'] = success()

            return res

        except:
            raise Exception
