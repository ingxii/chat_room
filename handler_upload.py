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
from urllib import urlencode  # p2 only


import json
from PIL import Image
from PIL import ImageFile
import tornado.websocket
import tornado.web
import tornado.gen
from tornado import httpclient
from tornado import escape
from tornado.httputil import url_concat
from tornado import httpclient
from tornado.options import define, options

# ud
from handler_base import BaseHandler, login_required, target_required, login_required_future
# from lib_api import WeChatAPI
# import ffmpeg

ImageFile.LOAD_TRUNCATED_IMAGES = True  # initialize   set


class UploadHandler(BaseHandler):

    def check_xsrf_cookie(self):
        '''for post from app'''
        pass

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*.ingxii.com')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*.ingxii.com')
        # self.set_header('Content-type', 'application/json')

    def get(self):
        self.set_secure_cookie("test", "123456")
        # self.set_secure_cookie("test", "123456", domain=options.cookie_domain)
        self.set_cookie("test_", "123456")
        # self.set_cookie("test_", "123456", domain=options.cookie_domain)
        self.write("hello")

    @login_required_future
    @tornado.gen.coroutine
    def post(self):
        t_p = ("static", "download")
        t_p_o = ("static", "download", "org")

        real_path = os.path.join(os.path.dirname(__file__), *t_p)
        real_path_org = os.path.join(os.path.dirname(__file__), *t_p_o)
        result = {"status": False}

        resourceid = self.get_argument("resourceid", False)

        try:
            if resourceid:
                pass

            else:

                list_of_img = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
                list_of_music = ['.mp3', '.aac', '.amr']
                fileinfo = self.request.files['file'][0]
                # print fileinfo.keys()
                # filetype = fileinfo['content_type']
                ext_name = os.path.splitext(fileinfo['filename'])[1]

                # image or music
                if ext_name in list_of_img:
                    # raise Exception()

                    # file local
                    # new filename
                    file_name = str(uuid.uuid4()) + ext_name
                    file_org = os.path.join(real_path_org, file_name)
                    file_new = os.path.join(real_path, file_name)

                    logging.warning("uploading " + file_org + "...")
                    with open(file_org, 'w') as out:
                        out.write(fileinfo['body'])

                    # create thumb image
                    logging.warning("saving " + file_new + "...")
                    img = Image.open(file_org)
                    img.save(file_org, quality=80)

                    # 保持缩略图
                    img.thumbnail((options.width_thumb, options.height_thumb), Image.ANTIALIAS)
                    img.save(file_new, quality=60)
                    img.close()

                    result['status'] = True
                    result['type'] = ext_name
                    result['src'] = "/".join(t_p + (file_name,))
                    result['org'] = "/".join(t_p_o + (file_name,))
                    result['height'] = img.height
                    result['width'] = img.width

                elif ext_name in list_of_music:
                    pass

                    # file_name = str(uuid.uuid4()) + ext_name
                    # file_music = os.path.join(real_path_org, file_name)

                    # logging.warning("uploading " + file_music + "...")
                    # with open(file_music, 'w') as out:
                    #     out.write(fileinfo['body'])

                    # result['status'] = True
                    # result['type'] = 'audio'
                    # result['data'] = "/".join(t_p + (file_name,))
                else:
                    logging.error("error type")
        except Exception as e:
            logging.error(e)
            pass

        self.finish(result)

    def function(self):
        pass
