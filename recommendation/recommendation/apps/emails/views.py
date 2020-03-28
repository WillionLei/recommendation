import json
import re

from django import http
from django.shortcuts import render

from celery_tasks.email.tasks import send_verify_email
from django.views import View

from users.models import User
from verifications.views import logger


class EmailView(View):
    """添加邮箱"""
    def post(self, request):
        email = request.POST.get('email')

        if not email:
            return http.HttpResponseForbidden('缺少必传参数')

        if not re.match(r'^[a-z0-9][\w\.\-]*.@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email错误')

        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code':400, 'ermsg':'添加失败'})
        verify_url = request.user.generate_veify_email()
        send_verify_email.delay(email, verify_url)

        return http.JsonResponse({'code':0, 'errmsg':'添加成功'})


class VerifyEmailView(View):
    """验证邮箱"""
    def put(self, request):
        token = request.GET.get('token')
        print("token:%s"%token)

        if not token:
            return http.HttpResponseBadRequest('缺少token')

        user = User.check_verify_email_token(token)

        if not user:
            return http.HttpResponseForbidden('无效的参数')

        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return  http.HttpResponseServerError('激活邮箱失败')

        return http.JsonResponse({'code':0,
                                  'errmsg':'ok'})


