# -*- coding:utf-8 -*-

from flask import render_template
from flask import json
from flask import request
from flask import session
from flask import Blueprint
from flask import redirect
from flask import g

from ..utils import login_required, APIConnector, callback_uri


mod = Blueprint('auth', __name__, static_folder='../static')


# GET /auth/fb
@mod.route('/fb')
def fb_login_client():
    return render_template('/auth/fb_login_redirect.html')


# GET /auth/fb/redirect
@mod.route('/fb/redirect')
@login_required
def fb_login_redirect():
    token = request.args.get('token')
    session['fb_token'] = token
    result = APIConnector().post('/auth/fb', data={'token': token})

    if not session.get('auth_redirect_url'):
        return redirect('/')
    else:
        redirect_url = session.get('auth_redirect_url')
        return redirect(redirect_url)


# GET /auth/list
@mod.route('/list')
def access():
    res = APIConnector().get('/auth/list')
    return render_template('/auth/auth.html', data=res['data'])


# GET /auth/status?user_id={}&dsource_id={}
@mod.route('/status')
def access_detail():
    dsource_id = request.args.get('dsource_id')
    res = APIConnector().get('/auth/status', params={'dsource_id': dsource_id})

    session['auth_redirect_url'] = '/auth/list?dsource_id=' + dsource_id

    for d in res['data']:
        d['redirect'] = callback_uri(d['credcol'])
    return render_template('/auth/auth_status.html', data=res['data'], redirect_to_fb=g.redirect_to_fb)

