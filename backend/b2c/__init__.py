# -*- coding:utf-8 -*-

from flask import Blueprint
from flask_restful import Api

import users
import mypage
import order
import service
import task

mod = Blueprint('b2c', __name__)
api = Api(mod, catch_all_404s=True)

api.add_resource(users.Delete, '/delete')
api.add_resource(users.SignIn, '/signin')
api.add_resource(users.SignUp, '/signup')
api.add_resource(users.Update, '/update')

api.add_resource(mypage.Purchase, '/mypage/purchase')
api.add_resource(mypage.PurchaseStatus, '/mypage/purchase/status')
api.add_resource(mypage.Report, '/mypage/purchase/report')

api.add_resource(order.CheckoutDeprecated, '/order/checkout')
api.add_resource(order.Checkout, '/order/checkout_task')
api.add_resource(order.Complete, '/order/completed')

api.add_resource(task.Survey,'/task/survey')

api.add_resource(service.Root, '/service/')
api.add_resource(service.Detail, '/service/detail')
api.add_resource(service.Suggestion, '/service/suggestion')

