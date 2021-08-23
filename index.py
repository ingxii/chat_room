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

import signal
import time
import os
import gc
import logging
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

# third part lib
import torndb
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.autoreload import add_reload_hook
from tornado.options import options


# user defined
import config
from handler_base import ErrorHandler, TestHandler
from handler_web import RoomHandler, LoginHandler, IndexHandler,KefuHandler,AdminHandler,LogoutHandler,ChatHandler
from handler_chat import SocketChatHandler
from handler_upload import UploadHandler


class Application(tornado.web.Application):

    def __init__(self):

        # debug
        logging.info(">" * 40)
        logging.info("listen on %d   ..." % options.port)

        self.listen(options.port)

        # initialize
        self.rooms = {}  # 缓存所有房间 {room_id:[user_id,user_id,user_id],room_id:[user_id,user_id,user_id],room_id:[user_id,user_id,user_id],...}
        self.users = {}  # 缓存所有用户 {user_id:{},user_id:{},user_id:{},user_id:{},user_id:{}}
        self.db = torndb.Connection(
            options.mysql_host, options.mysql_db, options.mysql_user, options.mysql_pass)

        handler = [
            (r"/chatsocket", SocketChatHandler),
            (r"/room", RoomHandler),
            (r"/upload", UploadHandler),
            (r"/kefu", KefuHandler),
            (r"/chat", ChatHandler),

            (r"/login", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/admin", AdminHandler),
            (r"/", IndexHandler),


            # (r"/group", GroupHandler),
            # (r"/friend", FriendHandler),
            # (r"/detail", DetailHandler),
            # (r"/user", UserHandler),
            # (r"/chat", ChatHandler),
            # (r"/new", NewHandler),
            # (r"/articles", ArticlesHandler),
            # (r"/test", TestHandler),
            (r".*", ErrorHandler),
        ]
        settings = dict(
            cookie_secret=options.cookie_secret,
            template_path=os.path.join(os.path.dirname(
                __file__), *("static", "templates")),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            debug=True,
        )
        tornado.web.Application.__init__(self, handler, **settings)

        # Application.count = Application.count +1
        # logging.info(Application.count)

    def close(self):
        self.db.close()
        logging.info("closed")


def main_stop(**kwargs):
    logging.info("stopping...")
    tornado.ioloop.IOLoop.current().stop()


def sig_handler(arg, frame):
    tornado.ioloop.IOLoop.current().add_callback(main_stop)


def main():
    tornado.options.parse_command_line()
    signal.signal(signal.SIGINT, sig_handler)
    # add_reload_hook(main_stop)

    Application.count = 1
    # start
    app = Application()
    tornado.ioloop.IOLoop.current().start()
    app.close()
    logging.info("stopped")


if __name__ == "__main__":
    main()
