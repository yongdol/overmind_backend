# -*- coding:utf-8 -*-

from flask import render_template
from flask import request
from flask import Blueprint
from flask import Flask, redirect

from ..utils import APIConnector
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Required

mod = Blueprint('service', __name__, static_folder='../static')


    
class SurveyForm(FlaskForm):
    industry = SelectField(u'업종 분류' ,choices=[(None, u'해당없음'),('A',u'농업,어업 및  임업'),('B',u'광업' ),('C',u'제조업'),('D',u'전기, 가스, 증기 및 수도사업'),\
                                      ('E',u'하수, 폐기물처리, 원료 재생 및 환경복원업'),('F',u'건설업'),('G',u'도매 및 소매업'),('H',u'운수업'),('I',u'숙박 및 음식점업'),\
                                      ('J',u'출판, 영상, 방송통신 및 정보서비스업'),('K',u'금융 및 보험업'),('L',u'부동산업 및 임대업'),('M',u'전문, 과학 및 기술서비스업'),\
                                      ('N',u'사업시설관리 및 사업지원서비스업'),('P',u'교육서비스업'),('Q',u'보건업 및 사회복지서비스업'),
                                      ('R',u'예술, 스포츠 및 여가관련 서비스업'),('S',u'협회 및 단체 수리및 기타 개인서비스업')])
    
    job_class = SelectField(u'직업 분류', choices=[(None,u'해당없음'),('1',u'관리자'),('2',u'전문가 및 관련 종사자'),('3',u'사무 종사자'),('4',u'서비스 종사자'),('5',u'판매 종사자'),\
                                        ('6',u'농림어업 숙련 종사자'),('7',u'기능원 및 관련기능 종사자'),('8',u'장치기계 조작 및 조립 종사자'),('9',u'단순노무 종사자')])
    
    E_type = SelectField(u'고용 형태',choices=[(None,u'해당없음'),('1',u'특수형태'),('2',u'재택/가내'),('3',u'파견'),('4',u'용역'),('5',u'일일'),('6',u'단시간'),('7',u'기간제'),\
                                         ('8',u'기간제아닌시한적'),('9',u'정규직')])
    
    sex = SelectField(u'성별', choices=[(None,u'해당없음'),('1',u'남자'),('2',u'여자')])
    
    education = SelectField(u'학력',choices=[(None,u'해당없음'),('1',u'중졸이하'),('2',u'고졸'),('3',u'초대졸'),('4',u'대졸'),('5',u'대학원졸이상')])
    
    age = StringField(u'연령')
    
    duration = SelectField(u'경력연수', choices=[(None,u'해당없음'),(1,u'1년미만'),(2,u'1년이상~2년미만'),(3,u'2년이상~3년미만'),(4,u'3년이상~4년미만'),\
                                          (5,u'4년이상~5년미만'),(6,u'5년이상~10년미만'),(7,u'10년이상')])
    
    W_type = SelectField(u'근무형태',choices=[(None,u'해당없음'),('1',u'교대제하지않음'),('2',u'2교대제'),('3',u'3교대제'),('4',u'격일제'),('5',u'단시간제')])
    
    submit = SubmitField(u'제출')
    
# GET /service/detail?service_id={}
@mod.route('/detail')
def info():
    service_id = request.args.get('service_id')
    res = APIConnector().get('/service/detail', params={'service_id': service_id})

    return render_template('/service/service_info.html', data=res['data'])


@mod.route('/survey',methods=['GET','POST'])

def survey():
    surform=SurveyForm()
    erm=None
    erm_si=u"나이는 정수형태여야 합니다. ex)1,2...32"
    data={}
    age=None
    if(request.method=="POST"):
        try: 
            if request.form.get('age')=="":
                age=None
            else:
                age=int(request.form.get('age'))
        except:
            return render_template('/service/survey.html', form=surform,erm=erm_si)
        
        data={'industry':request.form.get('industry') ,'job_class':request.form.get('job_class'),'E_type':request.form.get('E_type'),'sex':request.form.get('sex')\
              ,'education':request.form.get('education'),'age':age,'duration':request.form.get('duration'),'W_type':request.form.get('W_type')}
        
        APIConnector().post('/task/survey',data=data)
        
        return redirect('/order/?service_id=80032')
    
    else:
        return render_template('/service/survey.html',form=surform)


