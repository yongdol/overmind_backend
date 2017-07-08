# -*- coding:utf-8 -*-
from flask import Blueprint
from flask_restful import Api

from auth import Auth
from auth_status import AuthStatus
from fb import Fb
from fb_temp import FbTemp
from kftc import Kftc
from release import Release
from me import Me

mod = Blueprint('auth', __name__, url_prefix='/auth')
api = Api(mod)

api.add_resource(Auth, '/list')
api.add_resource(AuthStatus, '/status')
api.add_resource(Fb, '/fb')
api.add_resource(FbTemp, '/fbtemp')
api.add_resource(Kftc, '/kftc')
api.add_resource(Release, '/release')
api.add_resource(Me, '/me')
