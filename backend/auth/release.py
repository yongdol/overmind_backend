from flask import g
from flask import request
from flask_restful import Resource
from sqlalchemy.sql import text

from backend.util import jwt_required
from backend.errors import success, bad_request, not_found


# POST /auth/release
class Release(Resource):
    @jwt_required(scopes=None)
    def post(self, **kwargs):
        id, credcol = kwargs.get('user_id'), request.form.get('credcol')
        res = {}

        try:
            credcols = g.db.execute(text("SELECT DISTINCT credcol FROM mand_credcol")).fetchall()
            credcols = [i[0] for i in credcols]

            if credcol is None or credcol not in credcols:
                res['e_msg'] = bad_request('Invalid Credcol')
                return res

            rowcounted = g.db.execute(text("""DELETE FROM credential WHERE user_id=:id and cred_key=:cred_key """),
                                      id=id, cred_key=credcol).rowcount
            if rowcounted > 0:
                res['e_msg'] = success()
            else:
                res['e_msg'] = not_found('Token not found')

        except:
            raise Exception()

        return res
