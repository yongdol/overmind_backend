# -*- coding:utf-8 -*-
# imports
import os
import tempfile


class Config(object):
    # Application threads. A common general assumption is
    # using 2 per available processor cores - to handle
    # incoming requests using one and performing background
    # operations using the other.
    THREADS_PER_PAGE = 2

    # Enable protection agains *Cross-site Request Forgery (CSRF)*
    CSRF_ENABLED = True

    # Use a secure, unique and absolutely secret key for signing the data.
    CSRF_SESSION_KEY = 'key for testonly'

    # Choose a method to save session data with Flask-Session
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = tempfile.mkdtemp()

    # Base path in project
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Database Config
    # DATABASE_URI = 'mysql+pymysql://root:dydehfnl@localhost:3306/overmind?charset=utf8'
    DATABASE_URI = 'mysql://root:dydehfnl@localhost:3306/overmind?charset=utf8'

    # Testing, Debugging Config
    TESTING = False
    DEBUG = False


class DevelopmentConfig(Config):
    BACKEND_URL = 'http://localhost:5505/api'
    FRONTEND_URL = 'http://localhost:5505'

    # Default Config
    SECRET_KEY = 'key for testonly'
    DEBUG = True

    # Facebook Config
    FB_APP_CONFIG = {
        "client_id": 1768174320168306,
        "redirect_url": FRONTEND_URL + "/auth/fb",
        "app_secret": "729b2980178ea0de7a6be6794181a31b"
    }

    # Release Config
    RELEASE_SERVICE = {
        'facebook': 'fb_access_token'
    }

    # KFTC Config
    KFTC_CONFIG = {
        "api_url": 'https://testapi.open-platform.or.kr/v1.0',
        "client_id": 'l7xx39a4256af5ee4c58ac436c4085ea2ecc',
        "client_secret": '081672eb5fa14032b5b4d6c8d06d3f25'
    }

    # Redirect URIs
    REDIRECT_URIS = {
        'fb_access_token': FRONTEND_URL + '/auth/fb',
        'kftc_login_access_token': BACKEND_URL + '/auth/kftc',
        'kftc_inquiry_access_token': BACKEND_URL + '/auth/kftc'
    }


class ProductionConfig(Config):
    # Config for production
    DEBUG = False

    # Default Config
    SECRET_KEY = 'key for testonly'

    BACKEND_URL = 'https://api.frisk.rocks'
    FRONTEND_URL = 'http://www.frisk.rocks:5505/'

    # Facebook Config
    FB_APP_CONFIG = {
        "client_id": 1768174320168306,
        "redirect_url": FRONTEND_URL + "/auth/fb",
        "app_secret": "729b2980178ea0de7a6be6794181a31b"
    }

    # KFTC Config
    KFTC_CONFIG = {
        "api_url": 'https://testapi.open-platform.or.kr/v1.0',
        "client_id": 'l7xx39a4256af5ee4c58ac436c4085ea2ecc',
        "client_secret": '081672eb5fa14032b5b4d6c8d06d3f25'
    }

    # Redirect URIs
    REDIRECT_URIS = {
        'fb_access_token': FRONTEND_URL + '/auth/fb',
        'kftc_login_access_token': BACKEND_URL + '/auth/kftc',
        'kftc_inquiry_access_token': BACKEND_URL + '/auth/kftc'
    }


class TestingConfig(Config):
    # Config for testing
    TESTING = True

    # Test for user users
    USERNAME = 'newtestid'
    PASSWORD = '1234'

    # Test for open api
    FB_TOKEN = ''


config = {
    "default": "config.ProductionConfig",
    "development": "config.DevelopmentConfig",
    "production": "config.ProductionConfig",
    "testing": "config.TestingConfig"
}


def configure_app(app, settings):
    app.config.from_object(config[settings])
