#!/usr/bin/env python
# coding:utf-8

# import os
import logging
# import uuid
import random
import time

import urlparse   # python2.7


import tornado.websocket
import tornado.web
import tornado.gen
from tornado import escape
from tornado.options import options



class ChatSocketHandlerBase(tornado.websocket.WebSocketHandler):

    def __init__(self, application, request, **kwargs):
        '''replace with real ip'''
        tornado.websocket.WebSocketHandler.__init__(
            self, application, request, **kwargs)

        if 'X-Real-Ip' in self.request.headers:
            self.request.remote_ip = self.request.headers['X-Real-Ip']
        # logging.info("__init__")

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
    def rooms(self):
        return self.application.rooms

    @property
    def users(self):
        return self.application.users

    def update_connect(self, is_connect):
        self.db.update(

            'UPDATE users SET is_connect=%s WHERE user_id = %s LIMIT 1', is_connect, self.current_user)

    def disconnect(self, is_connect, user_id):
        self.db.update(
            'UPDATE users SET is_connect=%s WHERE user_id = %s LIMIT 1', is_connect, user_id)

    def check_origin(self, origin):
        '''
        Check domain. for websocket ONLY
        Do not forget dot(.)
        '''
        if options.DEBUG:
            return True

        # logging.info("check_origin base")
        parsed_origin = urlparse.urlparse(origin)
        # parsed_origin = urllib.parse.urlparse(origin)
        for domain in options.allowed_domain:
            if parsed_origin.netloc.endswith(domain):
                return True

        return False

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def load_room(self, room_id):
        members = []
        room_info = self.db.get(
            "SELECT * FROM user_rooms WHERE room_id = %s LIMIT 1", str(room_id))
        if room_info:
            members = str(room_info['members']).split(',')  # 结果['41','51']
            members = map(int, members)  # 字符串转整型ID
        return members

    def load_user(self, user_id):
        user = None
        user_info = self.db.get(
            "SELECT user_id,headimgurl,username FROM users WHERE user_id = %s LIMIT 1", str(user_id))
        if user_info:
            user = {
                'user_id': user_info['user_id'],
                'headimgurl': user_info['headimgurl'],
                'username': user_info['username'],
                'handler': None,
            }
        return user


    def format_msg(self, message):
        '''  format  ALL message  before send   '''

        chat = {
            "id": message['id'] if 'id' in message else 0,
            "add_time": message['add_time'] if 'add_time' in message else int(time.time()),
            "body": message['body'] if 'body' in message else "",
            "from": message["from"] if 'from' in message else 0,
            "type": message['type'] if 'type' in message else "text",
            "to": message['to'] if 'to' in message else 0,
        }

        # 文本消息
        if chat['type'] == "text":
            # chat['body'] = tornado.escape.linkify(chat['body'])
            pass

        # 非系统用户 则从获取用户的相信信息
        user_from = chat['from']
        if user_from:

            # 从数据库中加载用户基本信息到缓存
            if user_from not in self.users:
                user_info = self.load_user(user_from)
                self.users[user_from] = user_info

            if self.users[user_from]:
                # 格式化用户头像和名称
                chat['username'] = self.users[user_from]['username'] if self.users[user_from]['username'] else "[匿名用户]"
                chat['headimgurl'] = self.users[user_from]['headimgurl'] if self.users[user_from]['headimgurl'] else ""
            else:
                # 用户应该以及不存在或者无效了
                # logging.warn("用户(%s)无效" %(user_from))
                return False
        else:
            # 系统消息
            logging.info('系统消息:%s' % (chat['body']))
            pass

        return chat

    # 发送给当前连接
    def send_message(self, chat):
        chat = self.format_msg(chat)
        if not chat:
            return

        self.write_message(chat)

    # 发送给房间
    def boardcast_message(self, chat):
        chat = self.format_msg(chat)
        if not chat or 'to' not in chat or not chat['to']:
            return
        room_id = chat['to']
        logging.info('[%s]%s:%s:%s', chat['to'],
                     chat['from'], chat['type'], chat['body'])

        if room_id in self.rooms:
            # 将消息发送到房间的所有用户
            for user_id in self.rooms[room_id]:
                try:
                    if user_id in self.users and self.users[user_id]['handler']:
                        self.users[user_id]['handler'].write_message(chat)
                except tornado.websocket.WebSocketClosedError as e:
                    logging.error(e)
                    self.users[user_id]['handler'] = None
                    self.disconnect(0, user_id)
                    logging.error("用户%s已经从房间%s断开" % (user_id, room_id))

    @tornado.gen.coroutine
    def prepare(self):
        if not self.current_user:
            logging.info("no current_user")
            return self.finish()

        # 初始化用户信息
        self.prepare_user(self.current_user)

    def prepare_user(self, user_id):
        try:
            # 关闭上一次的连接
            if self.users and user_id in self.users and self.users[user_id]['handler']:
                self.users[user_id]['handler'].close()
                self.users[user_id]['handler'] = None
        except Exception as e:
            logging.info(e)

        # 从数据加载用户信息
        user_info = self.load_user(user_id)
        if not user_info:
            return False

        # socket 句柄,每个用户只保留一个连接
        user_info['handler'] = self
        self.users[self.current_user] = user_info

        return True

