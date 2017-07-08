# -*- coding:utf-8 -*-

from flask import request
from flask import jsonify
from flask_restful import Resource

from flask import g
from sqlalchemy import text, create_engine

from backend.util import jwt_required
from backend.util.task import check_service
from backend.errors import success
from backend.util.task import update_state
def nfil(x):
    if x =='None':
         return None
    else:
        return x
class Survey(Resource):
    
    @jwt_required(scopes=None)
    def post(self,**kwargs):
        
        res={}
        
        user_id=kwargs.get('user_id')    
    
        industry=nfil(request.form.get('industry'))
        job_class=nfil(request.form.get('job_class'))
        E_type=nfil(request.form.get('E_type'))
        sex=nfil(request.form.get('sex'))
        education=nfil(request.form.get('education'))
        age=nfil(request.form.get('age'))
        duration=nfil(request.form.get('duration'))
        W_type=nfil(request.form.get('W_type'))

        
        query="""
               INSERT INTO user_survey (user_id, industry, job_class, E_type, sex, education, age, duration, W_type)
               VALUES(:user_id, :industry, :job_class, E_type, sex, education, age, duration, W_type)
               ON DUPLICATE KEY UPDATE industry=:industry, job_class=:job_class,E_type=:E_type,sex=:sex, education=:education, age=:age, duration=:duration, W_type=:W_type 
              """
        try:
            g.db.execute(text(query), user_id=user_id, industry=industry, job_class=job_class, E_type=E_type, sex=sex, education=education, age=age, duration=duration, W_type=W_type)
        except Exception as e:
            raise Exception(e)
        
        
        update_state(user_id, 5, True, u'직업군 설문조사 완료') 
        
        res['e_msg']=success()
        
        return res
    


