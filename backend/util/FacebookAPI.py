# -*- coding:utf-8 -*-

import requests
import json


class Facebook:
    def __init__(self, token):
        """ class Facebook

    :params token: user token to initialize

    - self.headers: token embedded header

    """
        self.headers = {'Authorization': 'Bearer ' + token}

    def get(self, *paths, **kwargs):
        """self.get

    get facebook api

    :param *paths: user define path to get
    :param **kwargs: get argument

    :Example:
        fb = Facebook("mytoken")
        fb.get('me','posts',limit = 50)

    :return: json
    """
        if len(paths) > 0:
            url = makeUrl(paths)
            result = requests.get('https://graph.facebook.com/%s/' % url, headers=self.headers, params=kwargs)
        else:
            return "no url paths"

        result = json.loads(result.text, result.encoding)

        if result.get('paging'):
            self.nextItem = result.get('paging').get('next')
        return result

    def next(self):
        """

    set next to paging.next and return next page


    :retrun: next page
    :raise: False
    """
        if self.nextItem:
            url = self.nextItem.decode('string_escape').replace('\\', '')
            result = requests.get(url, headers=self.headers)
            result = json.loads(result.text, result.encoding)
            if result.get('paging'):
                self.nextItem = result.get('paging').get('next')
            else:
                self.nextItem = False
            return result
        else:
            return False

    def getAll(self, *paths, **kwargs):
        """

    get all next page while there isnt any.

    :return: next page
    :raise: False
    """
        result = []
        result.append(self.get(*paths, **kwargs))
        next = self.next()
        while next:
            result.append(next)
            next = self.next()
        return result

    def getAllData(self, *paths, **kwargs):
        """

    from json response, take 'data' value.
    and repeat until paging.next exists

    :return: [ 'data',...]
    """
        result = []
        result = result + self.get(*paths, **kwargs)['data']
        next = self.next()
        while next:
            result = result + (next['data'])
            next = self.next()
        return result

    def getLoop(self, id_array, *paths, **kwargs):
        """

    get loop from id_array

    :param id_array: array contains ids
    :param *path:
    :param **kwargs:

    :return: [ series of get result]
    """
        result = []
        if len(id_array) > 100:
            print 'warning, it could be extremely slow!!'
        for id in id_array:
            result.append(self.get(id, *paths, **kwargs))
        return result

    def takeIds(self, got):
        """

    from json response take id

    :return: [ids]
    """
        ids = []
        for item in got['data']:
            ids.append(item['id'])
        return ids

    def getLongToken(self, token, app_id, app_secret, redirect_uri):
        """
      change available token to long token

      :param token: token
      :param app_id: facebook app id
      :param app_secret: facebook app secret
      :param redirect_url: maybe doesn't matter ...unless you are not browser

      :return: long token
    """
        keys = {'grant_type': 'fb_exchange_token', 'client_id': app_id, 'client_secret': app_secret,
                'fb_exchange_token': token, 'redirect_uri': redirect_uri}
        result = requests.get('https://graph.facebook.com/oauth/access_token', params=keys)
        return result.text.replace('access_token=', '')


def makeUrl(paths):
    acc = ''
    for item in paths:
        acc += item + '/'
    return acc[0:-1]
