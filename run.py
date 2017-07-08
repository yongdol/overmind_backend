# -*- coding:utf-8 -*-

from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple
from backend.app import app as back
from frontend import app as front

# pyc file 만들지 않는 옵션
import os

os.environ['PYTHONDONTWRITEBYTECODE'] = 'x'

application = DispatcherMiddleware(front, {'/api': back})
run_simple('0.0.0.0', 5505, application, use_reloader=True, threaded=True, use_debugger=True)