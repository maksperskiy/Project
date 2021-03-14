from flask import request, make_response
from functools import wraps
from config import *


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == USER and auth.password == PASSWORD:
            return f(*args, **kwargs)
        return make_response('Неверный логин или пароль', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    return decorated
