# -*- coding:utf-8 -*-

from flask import render_template
from flask import json
from flask import request
from flask import session
from flask import Blueprint
from collections import OrderedDict
import json

from ..utils import login_required, APIConnector
from ..utils import format_parser

mod = Blueprint('mypage', __name__, static_folder='../static')


# Login checking
@mod.before_request
@login_required
def loggin_check():
    pass


# GET /mypage
@mod.route('/')
def main():
    return render_template('/mypage/index.html')


# GET /mypage/purchase?user_id=1
@mod.route('/purchase')
def purchase():
    res = APIConnector().get('/mypage/purchase')

    return render_template('/mypage/purchase.html', result=res['data'])


# GET /mypage/purchase/status?user_id=1&order_id=1
@mod.route('/purchase/status')
def purchase_status():
    order_id = request.args.get('order_id')

    if order_id is None:
        return render_template('/error.html', error='Order id not found')

    else:
        res = APIConnector().get('/mypage/purchase/status', params={'order_id': order_id})
        purchases = APIConnector().get('/mypage/purchase')

        # check whether it is finished or not
        status = filter(lambda x: str(x['id']) == order_id, purchases['data'])[0]['status']
        return render_template('/mypage/purchase_status.html', result=res['data'], status=status)


# GET /mypage/purchase/report?user_id=1&order_id=1
@mod.route('/purchase/report')
def purchase_report():
    order_id = request.args.get('order_id')
    res = APIConnector().get('/mypage/purchase/report', params={'job_id': order_id})

    result = json.loads(res['data'].get('big_json'), object_pairs_hook=OrderedDict)
    title, components = format_parser(result)

    return render_template('/mypage/report.html', job_id=order_id, title=title, components=components)


# GET /mypage/byebye
@mod.route('/byebye')
def bye():
    if session.get('access_token'):
        return render_template('/mypage/byebye.html')
    else:
        return render_template('/error.html', error='User not logged in')
