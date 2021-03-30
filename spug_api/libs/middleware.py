# coding=utf-8
from flask import request, make_response, g, redirect, send_from_directory
from libs.tools import json_response
from apps.account.models import User
from public import app
import time
import flask_excel as excel
from flask_login import login_user,current_user,login_manager,login_required
from libs.tools import json_response, JsonParser
import os


def init_app(app):
    excel.init_excel(app)
    app.before_request(cross_domain_access_before)
    app.before_request(auth_request_url)
    app.after_request(cross_domain_access_after)
    app.register_error_handler(Exception, exception_handler)
    app.register_error_handler(404, page_not_found)


def cross_domain_access_before():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'X-TOKEN'
        response.headers['Access-Control-Max-Age'] = 24 * 60 * 60
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
        return response


def cross_domain_access_after(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-TOKEN'
    return response


def page_not_found(_):
    return json_response(message='Resource not found'), 404


def exception_handler(ex):
    app.logger.exception(ex)
    message = '%s' % ex
    if len(message) > 60:
        message = message[:60] + '...'
    return json_response(message=message)


def auth_request_url():
    print("=========hahahahahah========",current_user.is_anonymous)
    print("====request.path====",request.path,current_user.is_authenticated,current_user.username)
    if not request.path.startswith("/schedule") and current_user.is_authenticated:
        return app.send_static_file("index.html")
    else:
        return None


