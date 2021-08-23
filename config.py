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
from tornado.options import define, options
define("DEBUG", default=True)

define("port", default=10001, help="run on the given port", type=int)

define("mysql_host", default="test0003.yzwgo.com:0000")
define("mysql_db", default="cn")
define("mysql_user", default="cn")
define("mysql_pass", default="123456")
define("cookie_token_name", default="user_id", help='tokenid name')

define("cookie_secret", default="_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__1")

define("cache_size", default=30,  type=int)

define("width_thumb", default=200.0, type=float)
define("height_thumb", default=600.0, type=float)
