# -*- coding:utf-8 -*-
from flask import Blueprint
from flask_restful import Api

import crawler
import receiver

mod = Blueprint('crawler', __name__, url_prefix='/crawler')
api = Api(mod)

api.add_resource(crawler.Crawler, '/get-a-job')
api.add_resource(receiver.Receiver, '/send-json-report')
