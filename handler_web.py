#!/usr/bin/env python
# coding=utf-8

import os
import logging
import uuid
import random
import time
import urllib
import random
import hashlib

from urllib import urlencode  # p2 only

import tornado.websocket
import tornado.web
import tornado.gen
import tornado.websocket
import tornado.web
import tornado.gen
from tornado import escape
from tornado.options import define, options
from tornado.httputil import url_concat
from tornado import httpclient

# user defined
from handler_base import BaseHandler, login_required, target_required, login_required_future


class LogoutHandler(BaseHandler):
    def get(self):
        self.logout()
        self.redirect('/login')


class LoginHandler(BaseHandler):
    ''' 登录页面 '''

    def login(self, email, password):
        user_info = self.get_user_by_email(email)

        if user_info:

            hasher = hashlib.md5()
            hasher.update(password)
            password = hasher.hexdigest()

            if user_info['password'] == password:
                self.current_user = int(user_info['user_id'])
                return user_info

        return False

    def get(self):
        # logging.info(self.current_user)
        # self.current_user = ("test%s" % random.randint(1000, 9999))
        # logging.info(self.current_user)
        self.render("login.html", email='', error='')

    def post(self):

        email = str(self.get_argument("email", ''))
        password = str(self.get_argument("password", ''))

        if self.login(email, password):
            self.redirect("/admin")
        else:
            self.render("login.html", email=email, error='账号或者密码错误')


class AdminHandler(BaseHandler):

    # 获取用户类型
    def get_roles(self, user_id):
        role_info = self.db.get(
            "SELECT * FROM roles WHERE user_id = %s LIMIT 1", str(user_id))
        # logging.info(role_info)
        result = role_info['role'] if role_info and 'role' in role_info else ''

        # return str(result).split(',') if result else []

        # 点分字符串转数组 并且去除空字符串
        result = [x for x in str(result).split(',') if x]
        return result

    # 获取当前用户类型
    @property
    def user_roles(self):
        return self.get_roles(self.current_user)

    def get_all_staff(self):

        sql = 'SELECT a.role,b.* FROM roles AS a JOIN users AS b ON a.user_id=b.user_id WHERE  role REGEXP "(^|,)staff(,|$)" LIMIT 100'
        result = self.db.query(sql)

        return result

    def get_settings(self):
        settings = self.db.get(
            "SELECT * FROM roles WHERE user_id = %s LIMIT 1", self.current_user)
        logging.info(settings)
        return settings

    def get(self):
        if not self.user_roles:
            return self.redirect('/login')

        if not 'admin' in self.user_roles and not 'staff' in self.user_roles:
            return self.error('权限不足')

        self.render("settings.html", staff=self.get_all_staff(), user=self.user,
                    settings=self.get_settings()) 
 
    @login_required  
    def post(self):
        if not self.user_roles:
            return self.redirect('/login')

        if not 'admin' in self.user_roles and not 'staff' in self.user_roles:
            return self.error('权限不足') 

        logging.info(self.request.arguments) 

        result = ''
        act = self.get_argument("act", False)

        if act == 'add':
            result = self.admin_add()
        elif act == 'set':
            result = self.admin_set()
        elif act == 'del':
            result = self.admin_del()
        else:
            pass

        if result:
            return self.error(result)
        else:
            self.redirect("/admin")
            # self.render("settings.html", staff=self.get_all_staff(), settings=self.get_settings())

    def admin_set(self):
        is_online = int(self.get_argument("is_online", 0))
        welcome = str(self.get_argument("welcome", ''))

        logging.info(is_online)
        self.db.update(
            'UPDATE roles SET is_online=%s,welcome=%s WHERE user_id = %s LIMIT 1', is_online, welcome, self.current_user)
        pass
      
    def admin_del(self):
        user_id = int(self.get_argument("user_id", 0))
        roles = self.get_roles(user_id)
        if user_id == self.current_user:
            return '不能删除自己'
              
        if roles and 'admin' in roles: 
            return '超级管理员不能删除'       

        if not 'admin' in self.user_roles:
            return self.error('权限不足')

        self.db.execute(
            'DELETE FROM users WHERE user_id = %s', user_id)
        self.db.execute(
            'DELETE FROM roles WHERE user_id = %s', user_id)
        pass

    def admin_add(self):
        email = str(self.get_argument("email", ''))
        role = str(self.get_argument("role", ''))
        username = str(self.get_argument("username", ''))
        password = str(self.get_argument("password", ''))

        if not email or not role or not username or not password:
            return "参数不能为空"

        if self.db.get(
                "SELECT * FROM users WHERE email = %s LIMIT 1", email):
            return "email已经存在"

        hasher = hashlib.md5()
        hasher.update(password)
        password = hasher.hexdigest()
        user_id = self.db.insert(
            "INSERT INTO users (`email`,`username`,`password`) VALUE (%s,%s,%s)", email, username, password)

        if not user_id:
            return "创建失败"

        logging.info(user_id)
        user_id = self.db.insert(
            "INSERT INTO roles (`user_id`,`role`,`is_online`) VALUE (%s,%s,%s)", user_id, role, 0)
        logging.info(user_id)

        return


class RoomHandler(BaseHandler):
    ''' 用来显示聊天页面 '''

    @login_required
    @target_required
    def get(self):
        # 给前端使用
        # logging.info(type(self.current_user))

        self.render("room.html",  current_room=self.current_room,
                    user=self.user)


class ChatHandler(BaseHandler):
    ''' 用来显示聊天页面 '''

    def get_rooms(self):
        sql = 'select * from user_rooms where members REGEXP "(^|,)%s(,|$)"'

        # 这里的current_user必须是int,不知道为什么.
        rooms = self.db.query(sql, int(self.current_user))
        if rooms:
            # for key, value in enumerate(rooms):
            #     rooms[key]['body'] = '[图片]' if value['type']  and value['type'] == 'image' else value['body']

            # logging.info(rooms)
            return rooms
        else:
            return []

    @login_required
    def get(self):
        rooms = self.get_rooms()
        # logging.info(rooms)

        self.render("chat.html",  user=self.user,  rooms=rooms)


class IndexHandler(BaseHandler):

    def get(self):

        self.render("index.html")


class KefuHandler(BaseHandler):

    def check_xsrf_cookie(self):
        '''禁用跨站检测'''
        pass

    def get_online_staff(self):
        result = self.db.get(
            'SELECT a.role,b.* FROM roles AS a JOIN users AS b ON a.user_id=b.user_id WHERE  role REGEXP "(^|,)staff(,|$)" and is_online=1 and  is_connect=1 ORDER BY RAND() LIMIT 1')
        return result

    # create random template user
    def create_user(self):
        email = ("test%s@ingxii.com" % random.randint(100000, 999999))
        username = '[匿名用户]'

        user_id = self.db.insert(
            "INSERT INTO users (`email`,`username`) VALUE (%s,%s)", email, username)
        self.current_user = int(user_id)

    # create random template user
    def create_room(self, members):
        room_id = 0

        # 成员ID排序 不像创建重复成员的房间时必须
        members.sort()
        # 拼接成字符串
        members = ','.join(str(id) for id in members)
        logging.info(members)

        room = self.db.get(
            "SELECT room_id FROM user_rooms   WHERE members=%s LIMIT 1", members)
        if room:
            room_id = room['room_id']
            logging.info(room_id)

        if not room_id:
            sql = "INSERT INTO user_rooms (`user_id`,`members`,`add_time`,`room_name`) VALUE (%s,%s,%s,%s)"
            room_id = self.db.insert(
                sql, self.current_user, members, int(time.time()), '[匿名用户]')
            logging.info(room_id)
        return room_id

    def get(self):
        staff = self.get_online_staff()
        if not staff:
            return self.error("坐席已满或者客服休息时间，请稍后再试！")

        # 创建临时用户
        if not self.current_user:
            self.create_user()
        if not self.current_user:
            return self.error('用户初始化失败')

        # 创建临时房间
        room_id = self.create_room(
            [int(self.current_user), int(staff['user_id'])])
        if not room_id:
            return self.error('聊天室初始化失败')

        self.redirect("/room?id=%s" % (room_id))

    # @user_login
    # @tornado.gen.coroutine
    # def post(self):

    #     self.redirect("/room?id=1")
    #     logging.info("post")
