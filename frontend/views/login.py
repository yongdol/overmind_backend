# -*- coding:utf-8 -*-

from flask import render_template
from flask import request
from flask import session
from flask import Blueprint
from flask import redirect
from flask import flash

from ..utils import login_required, LoginForm, login_form_validation, APIConnector


mod = Blueprint('users', __name__, static_folder='../static')


# GET /signout
@mod.route('/signout')
@login_required
def signout():
    session.pop('access_token')
    return redirect('/')


# GET /signin
@mod.route('/signin', methods=['GET'])
def intro():
    if request.method == 'GET':
        if session.get('access_token'):
            return redirect('/')
        form = LoginForm()
        return render_template("/users/signin.html", form=form)


# POST /signin
@mod.route('/signin', methods=["POST"])
@login_form_validation
def signin():
    if session.get('access_token'):
        return render_template("error.html", error="Already logged in")

    form = LoginForm()
    user_id = request.form.get('id')
    user_pw = request.form.get('pw')

    res = APIConnector().post('/signin', data={'id': user_id, 'pw': user_pw})

    session['access_token'] = res.get('access_token')
    session['refresh_token'] = res.get('refresh_token')
    return redirect(request.referrer)


# GET /signup
@mod.route('/signup')
def signup():
    if session.get('access_token'):
        return render_template("error.html", error="Already logged in")
    return render_template("/users/signup.html")


# POST /signup
@mod.route('/signup', methods=['POST'])
@login_form_validation
def local_signup():
    id, pw = request.form.get('id'), request.form.get('pw')
    res = APIConnector().post('/signup', data={'id': id, 'pw': pw})

    flash("Successfully sign-up, please login")
    return redirect('/users/signin')


# GET /fb
@mod.route('/fb')
def fb_login_client():
    return render_template('/auth/fb_login_redirect.html')


# GET /fb/redirect
@mod.route('/fb/redirect')
@login_required
def fb_login_redirect():
    token = request.args.get('token')
    session['fb_token'] = token
    res = APIConnector().post('/auth/fb/update', data={'token': token})


    if not session.get('auth_redirect_url'):
        return redirect('/')
    else:
        redirect_url = session.get('auth_redirect_url')
        session.pop('auth_redirect_url', None)
        return redirect(redirect_url)
