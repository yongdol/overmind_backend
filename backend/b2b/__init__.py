# -*- coding:utf-8 -*-

from flask import Blueprint
from flask_restful import Api

# from b2c import users
# from b2c import service
import pf
import members
import report

mod = Blueprint('b2b', __name__)
api = Api(mod, catch_all_404s=True)

api.add_resource(members.Delete, '/overmind/delete')
api.add_resource(members.OMSignIn, '/overmind/signin')
api.add_resource(members.OMSignUp, '/overmind/signup')
api.add_resource(members.Update, '/overmind/update')

api.add_resource(pf.Pflist, '/overmind/vc/pflist')
api.add_resource(pf.Pf, '/overmind/pflist/pf')
api.add_resource(pf.AddPf, '/overmind/addpf')

api.add_resource(report.Report, '/overmind/portco/report')
api.add_resource(report.FileUpload, '/overmind/fileupload')
