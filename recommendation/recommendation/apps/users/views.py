# import json
import re

from django import http
from django.contrib.auth import login, authenticate
from django.db.models.sql import constants
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection
from kombu.utils import json
from pymysql import DatabaseError

from users.models import User


class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, username):
        """
        :param request: get
        :param username: string
        :return: JSON
        """
        # 查找用户名在数据库中的数量

        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code':0,
                                  'errmsg':'OK',
                                  'count': count})


class MobileCountView(View):
    """判断手机号是否重复"""
    def get(self, request, mobile):
        """
        判断电话号是否重复，返回对应的个数
        :param request: get
        :param mobile: string
        :return: JSON
        """
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({
            'code':0,
            'errmsg':'ok',
            'count': count
        })


class RegisterView(View):
    """用户注册"""
    def post(self, request):
        # dict = json.loads(request.body).decode()
        username = request.POST.get('username')
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
        sms_code_client = request.POST.get('sms_code')

        print(username, password, mobile, allow, sms_code_client)

        if not all([username, password, mobile, allow, sms_code_client]):
            return http.HttpResponseForbidden('缺少必传参数')

        if not re.match(r'^[a-zA-Z0-9_-]{2,8}$', username):
            return http.HttpResponseForbidden('用户名格式错误')

        if not re.match(r'^[0-9A-Za-z]{8,16}$', password):
            return http.HttpResponseForbidden('密码格式错误')

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('手机号码格式错误')

        if allow != 'true':
            return http.HttpResponseForbidden('请阅读协议并勾选同意')

        if not re.match(r'^\d{6}$', sms_code_client):
            return http.HttpResponseForbidden('验证码错误')

        redis_connection = get_redis_connection('verify_code')

        sms_code_server = redis_connection.get('sms_code_%s' % mobile)

        if sms_code_server is None:
            return  http.HttpResponse(status=400)

        if sms_code_server != sms_code_client:
            return http.HttpResponse(status=400)

        try:
            user = User.objects.create_user(username=username,
                                            password=password,
                                            mobile=mobile)
            user.save()
        except DatabaseError:
            return http.HttpResponse(status=400)

        login(request, user)

        response = redirect('/')
        response.set_cookie('username',username, max_age=constants.USERNAME_COOKIE_EXPIRES)

        return response

    def get(self, request):
        return render(request, 'register.html')


class UserLoginView(View):
    '''登录接口'''
    def post(self, request):
        # dict = json.laods(request.body.decode())
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        if not all([username, password, remembered]):
            return http.HttpResponseForbidden('缺少必传参数')

        if not re.match(r'^[a-zA-Z0-9_]{3,8}$', username):
            return http.HttpResponseForbidden('用户名错误')

        if not re.match(r'^[0-9a-zA-Z]{8,16}$', password):
            return http.HttpResponseForbidden('密码错误')

        user = User.objects.get(username=username)
        print(user,user.password)
        user = authenticate(request, username=username, password=password)

        if user is None:
            return http.HttpResponseForbidden('用户不存在')

        login(request, user)
        if remembered != True:
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None)

        return http.JsonResponse({'code': 0, 'errmsg':'OK'})