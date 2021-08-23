#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Simplified chat demo for websockets.

Authentication, error handling, etc are left as an exercise for the reader :)


TODO:
"""

import os
import logging
import uuid
import random
import time
import urllib
import random
import datetime
import time

import urlparse  # python2.7


import json


import tornado.websocket
import tornado.web
import tornado.gen
from tornado import httpclient
from tornado import escape
from tornado.httputil import url_concat
from tornado import httpclient
from tornado.options import define, options


from urllib import urlencode  # p2 only


def login_required(fn):
    def _wrapper(self, *args, **kwargs):

        if self.current_user:
            fn(self, *args, **kwargs)
        else:
            logging.info("login_required bad")
            self.redirect("/login")
            return
    return _wrapper


def login_required_future(fn):
    @tornado.gen.coroutine
    def _wrapper(self, *args, **kwargs):
        if self.current_user:
            yield fn(self, *args, **kwargs)
        else:
            logging.info("login_required bad")
            self.redirect("/login")
            return
    return _wrapper


# 完成
def target_required(fn):
    def _wrapper(self, *args, **kwargs):
        target = int(self.get_argument("id", False))
        if target > 0:
            self.current_room = target
            fn(self, *args, **kwargs)
        else:
            logging.info("room_required bad")
            self.error("房间ID出错!")
            return
    return _wrapper

# 完成


# def user_login(fn):
#     def _wrapper(self, *args, **kwargs):
#         username = self.get_argument("username", False)
#         if username:
#             if len(username) > 32:
#                 logging.info("username is too long")
#                 self.error("用户名太长")
#                 return

#             user_id = self.db.insert(
#                 "INSERT INTO users (`username`) VALUE (%s)", username)
#             self.set_current_user(user_id)
#             fn(self, *args, **kwargs)
#         else:
#             logging.info("username is empty")
#             self.error("用户名为空")
#             return
#     return _wrapper


class BaseHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        '''replace with real ip'''
        tornado.web.RequestHandler.__init__(self, application, request,
                                            **kwargs)
        self._current_room = 0

        if 'X-Real-Ip' in self.request.headers:
            self.request.remote_ip = self.request.headers['X-Real-Ip']

    def set_default_headers(self):
        self.set_header('Server', 'Hello')

    def get_current_user(self):
        if self.get_secure_cookie(options.cookie_token_name):
            return self.get_secure_cookie(options.cookie_token_name)
        else:
            return None

    def set_current_user(self, uid):
        self.set_secure_cookie(options.cookie_token_name, str(uid))

    @property
    def current_user(self):
        if not hasattr(self, "_current_user"):
            self._current_user = self.get_current_user()
        else:
            pass

        # 处理后的结果
        return int(self._current_user or 0)

    @current_user.setter
    def current_user(self, value):
        self.set_current_user(value)
        self._current_user = value
        logging.warning('Set cookie ' + str(value))

    @property
    def db(self):
        return self.application.db

    @property
    def current_room(self):
        return self._current_room

    @current_room.setter
    def current_room(self, value):
        self._current_room = value

    def get_user_by_email(self, email):
        return self.db.get(
            "SELECT * FROM users WHERE email = %s LIMIT 1", str(email))

    def error(self, error):

        self.render("error.html", error=error)

    def logout(self):
        self.current_user = ''

    @property
    def user(self):
        return self.get_user(str(self.current_user))

    def get_user(self, user_id):
        user = {
            'user_id': 0,
            'is_online': 0,
            'is_connect': 0,
            'user_type': 0,
            'headimgurl': '',
            'username': '',
            'email': '',
            'role': '',
            'welcome': '',
        }

        if user_id:
            sql = "SELECT u.*,s.role,s.is_online,s.welcome FROM users AS u LEFT JOIN roles AS s ON s.user_id = u.user_id WHERE u.user_id = %s LIMIT 1"
            user_info = self.db.get(
                sql, str(user_id))

            if user_info:
                user = {
                    'user_id': int(user_info['user_id']) if user_info['user_id'] else 0,
                    'is_online': int(user_info['is_online']) if user_info['is_online'] else 0,
                    'is_connect': int(user_info['is_connect']) if user_info['is_connect'] else 0,
                    'user_type': int(user_info['user_type']) if user_info['user_type'] else 0,
                    'headimgurl': user_info['headimgurl'] if user_info['headimgurl'] else '',
                    'username': user_info['username'] if user_info['username'] else '',
                    'email': user_info['email'] if user_info['email'] else '',
                    'role': user_info['role'] if user_info['role'] else '',
                    'welcome': user_info['welcome'] if user_info['welcome'] else '',
                }

        user['role'] = [x for x in str(user['role']).split(',') if x]
        return user


class ErrorHandler(BaseHandler):

    def check_xsrf_cookie(self):
        '''for post from app'''
        pass

    @tornado.gen.coroutine
    def get(self):

        pass

    @tornado.gen.coroutine
    def prepare(self):
        self.write_error(404)
        pass


class TestHandler(BaseHandler):

    def check_xsrf_cookie(self):
        '''for post from app'''
        pass

    @tornado.gen.coroutine
    def prepare(self):
        # print '[arguments]' + str(self.request.arguments) + "\r\n"
        # print '[body]' + str(self.request.body) + "\r\n"
        # print '[body_arguments]' + str(self.request.body_arguments) + "\r\n"
        # print '[connection]' + str(self.request.connection) + "\r\n"
        # print '[cookies]' + str(self.request.cookies) + "\r\n"
        # print '[files]' + str(self.request.files) + "\r\n"
        # print '[finish]' + str(self.request.finish) + "\r\n"
        # print '[full_url]' + str(self.request.full_url) + "\r\n"
        # print '[get_ssl_certificate]' + str(self.request.get_ssl_certificate) + "\r\n"
        # print '[host]' + str(self.request.host) + "\r\n"
        # print '[method]' + str(self.request.method) + "\r\n"
        # print '[path]' + str(self.request.path) + "\r\n"
        # print '[protocol]' + str(self.request.protocol) + "\r\n"
        # print '[query]' + str(self.request.query) + "\r\n"
        # print '[query_arguments]' + str(self.request.query_arguments) + "\r\n"
        # print '[remote_ip]' + str(self.request.remote_ip) + "\r\n"
        # print '[request_time]' + str(self.request.request_time) + "\r\n"
        # print '[supports_http_1_1]' + str(self.request.supports_http_1_1) + "\r\n"
        # print '[uri]' + str(self.request.uri) + "\r\n"
        # print '[version]' + str(self.request.version) + "\r\n"
        # print '[write]' + str(self.request.write) + "\r\n"
        # self.finish("Error")
        # yield tornado.gen.sleep(1)
        # raise tornado.gen.Return(111)
        # raise  ValueError("121")
        # raise  KeyError("121")
        # self.finish('[headers]' + str(self.request.headers) + "\r\n")
        self.render("test.html")
