from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View

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