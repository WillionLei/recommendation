import logging
import random

from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

# from recommendation.recommendation.libs.captcha.captcha import captcha


from recommendation.libs.captcha.captcha import captcha
from celery_tasks.sms.tasks import ccp_send_sms_code
logger = logging.getLogger('django')


class ImageCodeView(View):
    """返回图形类验证码"""
    def get(self, request, uuid):
        """
        生成图形验证码，保存到redis中，另外返回图片
        :param request:
        :param uuid:浏览器端生成的唯一id
        :return:picture
        """
        text, code, image = captcha.generate_captcha()
        print(text,code)
        redis_connection = get_redis_connection('verify_code')

        redis_connection.setex('img_%s'% uuid, 300, code)

        return http.HttpResponse(image,
                                 content_type='image/jpg')


class SMSCodeView(View):
    """短信验证码"""
    def get(self, request, mobile):
        """

        :param request:
        :param mobile:
        :return: JSON
        """
        redis_connection = get_redis_connection('verify_code')

        send_flag = redis_connection.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code':400,'errmsg':'发送短信过于频繁'})

        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')
        if not all([image_code_client, uuid]):
            return http.JsonResponse({'code':400,
                                      'errmsg':'缺少必传参数'})

        image_code_server = redis_connection.get('img_%s' % uuid)
        if image_code_server is None:
            return http.JsonResponse({
                'code':400,
                'errmsg':'请填写图形验证码'
            })

        try:
            redis_connection.delete('img_%s' % uuid)
        except Exception as  e:
            logger.error(e)

        image_code_server = image_code_server.decode()
        print(image_code_server)
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({'code':400,'errmsg':'图形验证码错误'})

        sms_code = '%06d' % random.randint(0,999999)
        logger.info(sms_code)

        p1 =redis_connection.pipeline()
        p1.setex('sms_code_%s' % mobile, 300,sms_code)
        p1.setex('send_flag_%s' % mobile, 60, 1)
        p1.execute()

        ccp_send_sms_code.delay(mobile, sms_code)
        print(sms_code)

        return http.JsonResponse({'code':0,
                                  'errmsg':'发送短信成功'})