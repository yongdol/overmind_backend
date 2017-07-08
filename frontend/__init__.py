from flask import Flask
from flask import render_template
from flask import session
from flask import request
from flask import g
from flask import redirect, flash
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_session import Session

from utils import LoginForm, APIConnector, APIResponseError
from config import configure_app
from views import *

app = Flask(__name__, static_folder="./static")
csrf = CSRFProtect(app)
configure_app(app, 'default')
Session(app)

# Add blueprint
with app.app_context():
    app.register_blueprint(auth.mod, url_prefix='/auth')
    app.register_blueprint(login.mod, url_prefix='/users')
    app.register_blueprint(mypage.mod, url_prefix='/mypage')
    app.register_blueprint(service.mod, url_prefix='/service')
    app.register_blueprint(order.mod, url_prefix='/order')
    app.register_blueprint(ask.mod, url_prefix='/ask')


@app.before_request
def init_app():
    g.backend_url = app.config['BACKEND_URL']
    g.frontend_url = app.config['FRONTEND_URL']
    g.client_id = app.config.get('FB_APP_CONFIG').get('client_id')
    redirect_url = app.config.get('FB_APP_CONFIG').get('redirect_url')
    g.redirect_to_fb = 'https://www.facebook.com/v2.8/dialog/oauth?client_id=%s&redirect_uri=%s&response_type=token' % (g.client_id, redirect_url)


@app.route('/')
def main():
    if app.debug:
        print "=====debug mode at {}".format(__name__)
        print 'token id', session.get('access_token')

    res = APIConnector().get('/service')

    if not res['e_msg'].get('status') == 200:
        return render_template('/error.html', error=res['e_msg'])

    elif request.args.get('search') is not None:
        return render_template('/home.html', data=res['data'], search=request.args.get('search'))

    return render_template('/home.html', data=res['data'])


@app.errorhandler(403)
def forbidden(e):
    return render_template("/users/signin.html", form=LoginForm()), 403


@app.errorhandler(CSRFError)
def handle_csrf(e):
    return render_template("/error.html", error="CSRF error")


@app.errorhandler(APIResponseError)
def handle_badresponse(e):
    flash(e)
    return redirect(request.headers['referer'])


@app.errorhandler(Exception)
def unhandled_exception(e):
    app.logger.error('Unhandled Exception: %s', e)
    return render_template('/error.html', error="Unhandled error")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
