# -*- coding: utf-8 -*-

from flask import current_app as app
from datetime import datetime

import requests

from config import ProductionConfig as cfg


class KFTCAuth:
    API_URL = cfg.KFTC_CONFIG['api_url']
    REDIRECT_URI = cfg.REDIRECT_URIS['kftc_login_access_token']
    CLIENT_ID = cfg.KFTC_CONFIG['client_id']
    CLIENT_SECRET = cfg.KFTC_CONFIG['client_secret']

    def authorize_url(self):
        params = {
            'response_type': 'code',
            'client_id': self.CLIENT_ID,
            'redirect_uri': self.REDIRECT_URI,
            'scope': 'login',
            'client_info': ''  # redirect_uri로 보내지는 추가정보
        }

        return requests.get(self.API_URL[:self.API_URL.find('v')] + 'oauth/2.0/authorize', params=params).url

    def register_account_url(self):
        params = {
            'response_type': 'code',
            'client_id': self.CLIENT_ID,
            'redirect_uri': self.REDIRECT_URI,
            'scope': 'inquiry',  # 계좌 조회용 scope
            'client_info': ''
        }

        return requests.get(self.API_URL[:self.API_URL.find('v')] + 'oauth/2.0/register_account', params=params).url

    def authorize_account_url(self):
        params = {
            'response_type': 'code',
            'client_id': self.CLIENT_ID,
            'redirect_uri': self.REDIRECT_URI,
            'scope': 'inquiry',
            'client_info': ''
        }

        return requests.get(self.API_URL[:self.API_URL.find('v')] + 'oauth/2.0/authorize_account', params=params).url

    def get_token(self, code):
        data = {
            'code': code,
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
            'redirect_uri': self.REDIRECT_URI,
            'grant_type': 'authorization_code'
        }

        return requests.post(self.API_URL[:self.API_URL.find('v')] + 'oauth/2.0/token', data=data).json()

    def refresh_token(self, r_token):
        data = {
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
            'refresh_token': r_token,
            'scope': 'inquiry',
            'grant_type': 'refresh_token'
        }

        return requests.post(self.API_URL[:self.API_URL.find('v')] + 'oauth/2.0/token', data=data).json()


class KFTCAPI:
    API_URL = cfg.KFTC_CONFIG['api_url']
    REDIRECT_URI = cfg.REDIRECT_URIS['kftc_login_access_token']
    CLIENT_ID = cfg.KFTC_CONFIG['client_id']
    CLIENT_SECRET = cfg.KFTC_CONFIG['client_secret']

    def __init__(self, access_token):
        self.access_token = access_token

    def account_balance(self, fintech_use_num):
        params = {
            'fintech_use_num': fintech_use_num,  # 사용자의 계좌번호(개인정보) 유출을 막기위해 제공되는 가상번호
            'tran_dtime': self._now()
        }

        return self._get('/account/balance', params=params)

    def account_cancel(self, scope, fintech_use_num):
        data = {
            'false': 'true',
            'fintech_use_num': fintech_use_num
        }

        return self._post('/account/cancel', data=data)

    def account_transaction_list(self, fintech_use_num, from_date, to_date, page=None):
        params = {
            'fintech_use_num': fintech_use_num,
            'inquiry_type': 'A',  # 입출금 모두
            'from_date': from_date,
            'to_date': to_date,
            'sort_order': 'D',  # 'A': 오름차순, 'D': 내림차순
            'page_index': '{:05d}'.format(page) if page is not None else None,
            'tran_dtime': self._now()
        }

        if page is not None:
            return self._get('/account/transaction_list', params=params)
        else:  # page is None
            page = 1
            params['page_index'] = '{:05d}'.format(page)
            response = self._get('/account/transaction_list', params=params)

            while response['next_page_yn'] == 'Y':
                page += 1
                params['page_index'] = '{:05d}'.format(page)

                next_page = self._get('/account/transaction_list', params=params)
                response['res_list'] += next_page['res_list']
                response['next_page_yn'] = next_page['next_page_yn']

            del response['page_index']
            del response['page_index_use_yn']
            del response['page_record_cnt']
            del response['next_page_yn']

            return response

    def bank_status(self):
        return self._get('/bank/status')

    def user_me(self, user_seq_no):
        params = {
            'user_seq_no': user_seq_no
        }

        return self._get('/user/me', params=params)

    def _get(self, path, params=None):
        headers = {'Authorization': 'Bearer ' + self.access_token} if self.access_token is not None else None
        response = requests.get(self.API_URL + path, params=params, headers=headers).json()
        if response['rsp_code'] != 'A0000':
            raise Exception(
                '{}::{}'.format(response['rsp_code'].encode('utf-8'), response['rsp_message'].encode('utf-8')))

        return response

    def _post(self, path, data=None):
        headers = {'Authorization': 'Bearer ' + self.access_token} if self.access_token is not None else None
        response = requests.post(self.API_URL + path, data=data, headers=headers).json()
        if response['rsp_code'] != 'A0000':
            raise Exception(
                '{}::{}'.format(response['rsp_code'].encode('utf-8'), response['rsp_message'].encode('utf-8')))

        return response

    def _now(self):
        return datetime.now().strftime('%Y%m%d%H%M%S')
