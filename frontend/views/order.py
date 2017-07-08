# -*- coding:utf-8 -*-

from flask import render_template
from flask import request
from flask import session
from flask import Blueprint
from flask import g
import datetime

from ..utils import login_required, APIConnector
from frontend.utils import task_uri


mod = Blueprint('order', __name__, static_folder='../static')


@mod.before_request
@login_required
def login_check():
    pass


# GET /order/completed?user_id={}&service_id={}
@mod.route('/completed')
def completed():
    res = {'data': {}}
    service_id = request.args.get('service_id')
    res_complete = APIConnector().post('/order/completed', data={'service_id': service_id})
    suggested = APIConnector().get('/service/suggestion', params={'service_id': service_id})

    res_info = APIConnector().get('/service/detail', params={'service_id': service_id})

    res['data']['dimg'] = res_info['data']['dimg']
    res['data']['service_name'] = res_info['data']['service_name']
    res['data']['dimg'] = res_info['data']['dimg']
    res['data']['status'] = 'waiting'
    res['data']['id'] = res_complete['data']['id']
    res['data']['order_time'] = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")

    return render_template('/order/completed.html', result=res['data'], suggested=suggested['data'])


# POST /order?service_id={}?user_id={}
@mod.route('/')
def checkout():
    service_id = request.args.get('service_id')
    session['auth_redirect_url'] = '/order?service_id={}'.format(service_id)
    data = APIConnector().get('/order/checkout_task', params={'service_id': service_id})['data']

    done = list()
    mandatory = list()
    elective = list()
    unable = list()

    for task in data:
        task['task_uri'] = task_uri(task['id'], service_id)
        if task['is_done']:
            done.append(task)
        else:
            # if some prerequsite tasks are not done
            if False in [pqt['is_done'] for pqt in list(filter(lambda x: x['id'] in task['prerequsite'], data))]:
                unable.append(task)
            else:
                if task['is_mandatory']:
                    mandatory.append(task)
                else:
                    elective.append(task)

    # if every mandatory task is done --> True, else --> False
    go_next = True \
        if False not in [mndt['is_done'] for mndt in list(filter(lambda x: x['is_mandatory'], data))] else False

    return render_template('/order/checkout.html', done=done,
                           mandatory=mandatory, elective=elective, unable=unable,
                           go_next=go_next, service_id=service_id)
