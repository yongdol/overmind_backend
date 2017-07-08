from flask import current_app


class ValidationError(ValueError):
    pass


def success(message='success'):
    res = {'status': 200, 'error': message}
    return res


def not_modified():
    res = {'status': 304, 'error': 'not modified'}
    return res


def bad_request(message):
    res = {'status': 400, 'error': 'bad request', 'message': message}
    return res


def unauthorized(message=None):
    if message is None:
        if current_app.config['USE_TOKEN_AUTH']:
            message = 'Please authenticate with your token.'
        else:
            message = 'Please authenticate.'

    res = {'status': 401, 'error': 'unauthorized', 'message': message}
    return res


def not_found(message):
    res = {'status': 404, 'error': 'not found', 'message': message}
    return res


def not_allowed(message):
    res = {'status': 405, 'error': 'method not allowed', 'message': message}
    return res


def precondition_failed():
    res = {'status': 412, 'error': 'precondition failed'}
    return res


def too_many_requests(message='You have exceeded your request rate'):
    res = {'status': 429, 'error': 'too many requests', 'message': message}
    return res


def internal_server_error(message):
    res = {'status': 500, 'error': 'Oops, something went terribly wrong!', 'message': message}
    return res
