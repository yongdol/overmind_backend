# -*-coding:utf-8-*-

import base64
import datetime
import smtplib
import traceback
from email.mime.text import MIMEText
from functools import wraps

import jwt
from Crypto import Random
from Crypto.Cipher import AES
from flask import request, g
from jwt import exceptions
from sqlalchemy import text

from config import ProductionConfig as cfg
#from config import DevelopmentConfig as cfg


# Function(decorator), **kwarg: secret key
def jwt_required(scopes=None):
    secret = cfg.SECRET_KEY

    if not secret:
        raise exceptions.InvalidKeyError

    def wrapper(f):
        @wraps(f)
        def decorated_function(*argv, **kwarg):
            token = request.headers.get("Authorization")
            if not token:
                raise exceptions.InvalidTokenError('Invalid Token')
            try:
                token = token.replace("JWT", "")

            except:
                raise Exception('Token scheme invalid')

            try:
                payload = jwt.decode(token, secret)
                if payload.get('type') == "REFRESH":
                    raise exceptions.InvalidTokenError('Invalid Token')

            except exceptions.DecodeError:
                traceback.print_stack()

            except exceptions.ExpiredSignatureError:
                traceback.print_stack()

            if scopes:
                if not payload.get('scopes'):
                    raise exceptions.MissingRequiredClaimError('Missing Required Claim')
                try:
                    user_scopes = list(payload.get('scopes'))
                except:
                    raise exceptions.MissingRequiredClaimError('Missing Required Claim')

                for item in user_scopes:
                    if item in scopes:
                        return f(*argv, user_id=payload.get('user_id'), **kwarg)

            return f(*argv, user_id=payload.get('user_id'), **kwarg)
        return decorated_function
    return wrapper


# Return access token
def jwt_access_token(user_id, expire, secret, scopes):

    # TODO: Check scope list

    payload = dict(
        user_id=user_id,
        scopes=scopes,
        exp=datetime.datetime.utcnow() + datetime.timedelta(seconds=expire),
        type="ACCESS"
    )
    access_token = jwt.encode(payload, secret)
    return access_token


# Return refresh token
def jwt_refresh_token(user_id, scopes, secret):

    # TODO: Check scope list

    payload = dict(
        user_id=user_id,
        scopes=scopes,
        type="REFRESH"
    )
    refresh_token = jwt.encode(payload, secret)
    return refresh_token


# Check user from token
def jwt_user_verify(token, secret):
    try:
        user_id = jwt.decode(token, secret, verify=False).get('user_id')
        query = "SELECT cred_value FROM credential WHERE user_id=:id AND cred_key='login_refresh_token'"
        refresh_token = g.db.execute(text(query), id=user_id).fetchone()[0]

        if token == refresh_token:
            return user_id
        else:
            return False
    except:
        raise Exception


# Check scope from token
def jwt_scope_verify(token, secret):
    scopes = jwt.decode(token, secret, verify=False).get('scopes')
    if scopes is None:
        raise exceptions.MissingRequiredClaimError
    else:
        return True


# Check token is valid
def jwt_token_verify(token, secret):
    type = jwt.decode(token, secret, verify=False).get('type')
    if type == "REFRESH":
        if jwt_user_verify(token, secret) & jwt_scope_verify(token, secret):
            return True

    elif type == "ACCESS":
        if jwt_scope_verify(token, secret):
            return True

    return False


class send_mail(object):
    def __init__(self, id, pw):
        self.id = id
        self.pw = pw
        self.smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        self.smtp.login(id, pw)

    def send(self, f, title, msg):
        msg = MIMEText(msg)
        msg['Subject'] = title
        msg['From'] = f
        msg['To'] = self.id
        self.smtp.sendmail(f, self.id, msg.as_string())


class FriskEncrypt:
    def __init__(self, key):
        BS = 16
        self.pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        self.unpad = lambda s: s[0:-ord(s[-1])]

        self.key = key

    def encrypt(self, string):
        raw = self.pad(string)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, string):
        string = base64.b64decode(string)
        iv = string[:16]
        enc = string[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        return self.unpad(cipher.decrypt(enc))
