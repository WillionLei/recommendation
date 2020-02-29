from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View

from users.models import User


class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request,username):
        """
        :param request: 请求对象
        :param username: 用户名
        :return: JSON
        """
        #查找用户名在数据库中的数量
        count = User.objects.filter(username).count()
        return http.JsonResponse({'code':0,
                                  'errmsg':'OK',
                                  'count':count})

