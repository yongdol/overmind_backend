from functools import wraps
from flask import flash, redirect, session, g, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length

import markdown2
import jwt
import requests
import json
import base64
import urllib
import time

from config import ProductionConfig as cfg



from backend.util import jwt_access_token, FriskEncrypt


# Parsing report format
def format_parser(data):
    title = data['title']
    form = {'markdown': [], 'table': [], 'graph': []}
    components = []
    for i in range(len(data['body'])):
        # Check format type
        if data['body'][i].get('form') == 'markdown':
            form['markdown'].append(markdown2.markdown(data['body'][i].get('markdown')))
        elif data['body'][i].get('form') == 'table':
            data['body'][i].update({'len': len(data['body'][i].get('data')[0].values()[0])})
            form['table'].append(data['body'][i])
        elif data['body'][i].get('form') == 'graph':
            data['body'][i].update({'index': i})
            form['graph'].append(data['body'][i])
        components.append(form)
        form = {'markdown': [], 'table': [], 'graph': []}
    return title, components


def login_required(f):
    @wraps(f)
    def decorated_function(*argv, **kwarg):
        if session.get('access_token'):
            return f(*argv, **kwarg)
        else:
            flash('User not logged in')
            return render_template("/users/signin.html", form=LoginForm()), 403

    return decorated_function


def login_form_validation(f):
    @wraps(f)
    def decorated_function(*argv, **kwarg):
        form = LoginForm()
        if form.validate_on_submit():
            return f(*argv, **kwarg)
        else:
            flash("Invalid users form!")
            return redirect("/users/signin")

    return decorated_function


def decode_token(token):
    return jwt.decode(token, cfg.SECRET_KEY)


def get_userid():
    if session.get('access_token'):
        return decode_token(session.get('access_token'))['user_id']
    else:
        return ''


def get_request_header():
    return {'Authorization': 'JWT {}'.format(session.get('access_token'))}


def callback_uri(credcol, service_id):
    if credcol == u'fb_access_token':
        args = {
            'client_id': cfg.FB_APP_CONFIG['client_id'],
            'redirect_uri': cfg.REDIRECT_URIS[credcol],
            'response_type': 'token',
            'scope': 'user_posts,email'
        }

        return 'https://www.facebook.com/v2.8/dialog/oauth?' + urllib.urlencode(args)

    elif credcol == u'kftc_login_access_token':
        api_url = cfg.KFTC_CONFIG['api_url']
        rd_url = api_url[:api_url.find('v')] + 'oauth/2.0/authorize?'

        crypt = FriskEncrypt(cfg.SECRET_KEY)
        data = {
            'user_id': get_userid(),
            'service_id': service_id,
            'now': str(int(time.time()))
        }

        client_info = {
            'requester': 'friskweb_t',
            'data': crypt.encrypt(json.dumps(data))
        }

        args = {
            'scope': 'login',
            'redirect_uri': cfg.REDIRECT_URIS['kftc_login_access_token'],
            'response_type': 'code',
            'client_id': cfg.KFTC_CONFIG['client_id'],
            'client_info': base64.urlsafe_b64encode(json.dumps(client_info))
        }

        return rd_url + urllib.urlencode(args)

    elif credcol == u'kftc_inquiry_access_token':
        api_url = cfg.KFTC_CONFIG['api_url']
        rd_url = api_url[:api_url.find('v')] + 'oauth/2.0/authorize_account?'

        crypt = FriskEncrypt(cfg.SECRET_KEY)
        data = {
            'user_id': get_userid(),
            'service_id': service_id,
            'now': str(int(time.time()))
        }

        client_info = {
            'requester': 'friskweb_t',
            'data': crypt.encrypt(json.dumps(data))
        }

        args = {
            'scope': 'inquiry',
            'redirect_uri': cfg.REDIRECT_URIS['kftc_login_access_token'],
            'response_type': 'code',
            'client_id': cfg.KFTC_CONFIG['client_id'],
            'client_info': base64.urlsafe_b64encode(json.dumps(client_info))
        }

        return rd_url + urllib.urlencode(args)
    
    else:
        return cfg.FRONTEND_URL



def task_uri(task_id, service_id):
    if task_id in range(3):
        return callback_uri({
            1: 'fb_access_token',
            2: 'kftc_login_access_token',
            3: 'kftc_inquiry_access_token'
        }.get(task_id), service_id)
    
    elif task_id == 5:
        return cfg.FRONTEND_URL+'service/survey'


class APIConnector:
    def get(self, path, params=None):
        headers = self._request_header if session.get('access_token') else None
        try:
            result = requests.get(g.backend_url + path, params=params, headers=headers).json()
        except:
            raise Exception('API Connection Failed')

        if result['e_msg']['status'] is not 200:
            raise APIResponseError('{}: {}'.format(result['e_msg']['error'], result['e_msg']['message']))

        return result

    def post(self, path, data=None):
        headers = self._request_header if session.get('access_token') else None
        try:
            result = requests.post(g.backend_url + path, data=data, headers=headers).json()
        except:
            raise Exception('API Connection Failed')

        if result['e_msg']['status'] is not 200:
            raise APIResponseError('{}: {}'.format(result['e_msg']['error'], result['e_msg']['message']))

        return result

    @property
    def _request_header(self):
        return {'Authorization': 'JWT {}'.format(session.get('access_token'))}

    def _refresh_token(self):
        session['access_token'] = jwt_access_token(get_userid(), 31536000, cfg.SECRET_KEY, 'master')


class APIResponseError(Exception):
    pass


class LoginForm(FlaskForm):
    id = StringField('id', validators=[DataRequired(), Length(min=1, max=20)])
    pw = PasswordField('pw', validators=[DataRequired(), Length(min=4, max=20)])
