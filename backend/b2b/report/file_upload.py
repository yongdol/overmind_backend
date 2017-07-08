# -*- coding:utf-8 -*-
from flask import request
from flask_restful import Resource


# POST /overmind/fileupload
class FileUpload(Resource):
    def post(self):
        fid = request.form.get('fid')
        print "file_name : %s" % fid
        res = fid
        return res
