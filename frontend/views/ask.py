# -*- coding:utf-8 -*-

from flask import render_template
from flask import request
from flask import Blueprint

from ..utils import APIConnector

mod = Blueprint('ask', __name__, static_folder='../static')


# GET /ask
@mod.route('/')
def main():
    error = request.args.get('error')
    return render_template('/ask/main.html', error=error)


# POST /ask/after
@mod.route('/after', methods=['POST'])
def after():
    email = request.form['email']
    message = request.form['message']
    params = {'email': email, 'message': message}

    res = APIConnector().get('/ask/after', params=params)

    return render_template("/ask/after.html")
