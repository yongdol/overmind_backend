from flask import Flask
from flask import g
from flask_cors import CORS
from sqlalchemy import create_engine

from config import configure_app

from auth import mod as auth
from b2c import mod as b2c
from crawler import mod as crawler
from b2b import mod as b2b
from errors import internal_server_error

import json


# def create_app(settings='default'):
app = Flask(__name__)
configure_app(app, 'default')
cors = CORS(app, resources={r"/.*": {"origins": r".*\.amazonaws\.com"}})

# Add blueprint
with app.app_context():
    app.register_blueprint(auth)
    app.register_blueprint(b2c)
    app.register_blueprint(crawler)
    app.register_blueprint(b2b)



@app.before_request
def open_db():
    try:
        g.db = create_engine(app.config['DATABASE_URI'], convert_unicode=True).connect()
    except:
        raise Exception('DB Connection Error')

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@app.teardown_request
def close_db(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.errorhandler(Exception)
def unhandled_exception(e):
    app.logger.error('Unhandled Exception: %s', e)
    return json.dumps({'e_msg': internal_server_error('Unhandled Exception')})

# return app
