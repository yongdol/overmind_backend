# -*- coding:utf-8 -*-
import requests, json

headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZXMiOiJtYXN0ZXIiLCJ0eXBlIjoiQUNDRVNTIiwiZXhwIjoxNTIxMDEyNDU2LCJ1c2VyX2lkIjoxNjl9.NlNUZlyimQYt5jWQihxryrHhCqEa_b8G-7PR8lTMtMo'}
params = {'service_id' : '80004'}
r = requests.get('http://ec2-13-124-49-237.ap-northeast-2.compute.amazonaws.com:5000/api/crawler/job_info', headers=headers, params=params)

print(r.content)