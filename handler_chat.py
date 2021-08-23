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


from handler_base import login_required, login_required_future
from handler_socket import ChatSocketHandlerBase

"""
socket handler
"""


def check_msg(fn):
    def _wrapper(self, message, *args, **kwargs):

        chat = escape.json_decode(message)

        # check message
        if not 'to' in chat or not chat['to']:
            logging.error("target error")
            return

        if not 'body' in chat:
            chat['body'] = ''

        chat['from'] = int(self.current_user)
        chat['to'] = int(chat['to'])

        return fn(self, chat, *args, **kwargs)

    return _wrapper


class SocketChatHandler(ChatSocketHandlerBase):

    """ room   """

    def initialize(self, **setting):
        # logging.info(setting)
        pass

    def on_close(self):
        logging.info(str(self.current_user) + " on_close")
        self.update_connect(0)

    @tornado.gen.coroutine
    def open(self):
        logging.info(str(self.current_user) + " open")
        self.update_connect(1)
        pass

    @check_msg
    def on_message(self, chat):
        '''  get new message  '''
        room_id = chat['to']
        save_message = True

        if room_id not in self.rooms:
            self.rooms[room_id] = self.load_room(room_id)

        if chat['type'] == 'enter':
            # 此消息将通知聊天室中的所有人
            # TODO:是否允许强行进入某聊天室
            if not self.break_door(room_id):
                logging.error("用户%s进入聊天室%s失败" % (self.current_user, room_id))
                return

            # 加载历史消息
            self.load_history_message(room_id)
            save_message = False
        elif chat['type'] == 'history':
            self.load_history_message(room_id, chat['body'])
            save_message = False
            return
        elif chat['type'] == 'image':
            chat['body'] = escape.json_encode(chat['body'])
        else:
            pass

        # 需要记录的消息
        if save_message:
            sql = "INSERT INTO messages (`from`, `to`, `type`, `body`) VALUE (%s,%s,%s,%s)"
            chat['id'] = self.db.insert(
                sql, chat['from'], room_id, chat['type'], chat['body'])

        # 轮发消息
        self.boardcast_message(chat)

    # 把当前连接强行加入房间
    def break_door(self, room_id):
        room_id = int(room_id)
        if not room_id > 0:
            return False

        if not self.current_user in self.rooms[room_id]:
            self.rooms[room_id].append(self.current_user)

        logging.info(self.rooms[room_id])
        return True

    def load_history_message(self, room_id, msg_id=0):
        room_id = int(room_id)
        msg_id = int(msg_id)

        if msg_id == 0:
            sql = "SELECT * FROM messages  WHERE `to`=%s ORDER BY message_id DESC LIMIT %s " % (
                room_id,  options.cache_size)
        else:
            sql = "SELECT * FROM messages  WHERE `to` = %s AND message_id < %s ORDER BY message_id DESC LIMIT %s " % (
                room_id, msg_id, options.cache_size)

        messages = self.db.query(sql)

        # messages.reverse()
        for message in messages[::-1]:
            # try:
            message['add_time'] = time.mktime(message['add_time'].timetuple())
            message['id'] = message['message_id']
            self.send_message(message)
            # except Exception as e:
            #     logging.error(e)
            #     pass
