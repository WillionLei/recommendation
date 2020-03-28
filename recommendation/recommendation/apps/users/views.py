# import json
import re

from django import http
from django.contrib.auth import login, logout, authenticate
from django.db.models.sql import constants
from django.shortcuts import render, redirect

from django.views import View
from django_crontab.crontab import logger
from django_redis import get_redis_connection
from kombu.utils import json
from pymysql import DatabaseError

from films.models import Film
from recommendation.utils.views import LoginRequiredMixin
from users.models import User, Collection


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
        response.set_cookie('username', username, max_age=constants.USERNAME_COOKIE_EXPIRES)

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

        # if not re.match(r'^[a-zA-Z0-9_]{3,8}$', username):
        #     return http.HttpResponseForbidden('用户名错误')

        if not re.match(r'^[0-9a-zA-Z]{8,16}$', password):
            return http.HttpResponseForbidden('密码错误')

        # user = User.objects.get(username=username)
        # print(user,user.password)
        user = authenticate(request, username=username, password=password)
        if user is None:
            return http.HttpResponseForbidden('用户不存在')

        login(request, user)
        if remembered != True:
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None)

        response = http.JsonResponse({'code':0, 'errmsg':'ok'})
        response.set_cookie('username',user.username, max_age=3600*24*14)

        return response


class LogoutView(View):
    """退出登录"""
    def delete(self, request):
        logout(request)
        response = http.JsonResponse({'code':0, 'errmsg':'ok'})
        response.delete_cookie('username')
        return response


class UserInfoView(LoginRequiredMixin, View):
    """用户中心"""
    def get(self, request):
        if request.user.is_authenticated():
            # 获取界面需要的数据,进行拼接
            info_data = {
                'username': request.user.username,
                'birthday': request.user.birthday,
                'mobile': request.user.mobile,
                'email': request.user.email,
                'email_active': request.user.email_active
            }

            # 返回响应
            return http.JsonResponse({'code': 0,
                                      'errmsg': 'ok',
                                      'info_data': info_data})


class ChangePwdView(View):
    # 修改密码
    def put(self, request):
        json_dict = json.loads(request.body.decode())
        old_password = json_dict.get('old_password')
        new_password = json_dict.get('new_password')
        new_password2 = json_dict.get('new_password2')

        # 校验参数
        if not all([old_password, new_password, new_password2]):
            return http.HttpResponseForbidden('缺少必传参数')

        result = request.user.check_password(old_password)
        if not result:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '原始密码不正确'})

        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return http.HttpResponseForbidden('密码最少8位，最长20位')

        if new_password != new_password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')

        # 修改密码
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': 400,
                                      'errmsg': 'ok'})

        # 清理状态保持信息
        logout(request)
        response = http.JsonResponse({'code': 0,
                                      'errmsg': 'ok'})

        response.delete_cookie('username')

        # # 响应密码修改结果：重定向到登录界面
        return response


class ChangeBirthday(View):
    # 修改生日
    def put(self, request):
        json_dict = json.loads(request.body.decode())
        birthday = json_dict.get('birthday')
        if not birthday:
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            # 修改生日
            request.user.email = birthday


            # 修改权限


            request.user.save()
        except Exception as  e:
            logger.error(e)
            return http.JsonResponse({'code':400, 'errmsg':'ok'})

        return http.JsonResponse({'code':400, 'errmsg':'ok'})


class AddCollections(View):
    def post(self, request):
        """ 新增收藏 """
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')
        if not title:
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            film = Film.objects.get(title=title)
        except Film.DoesNotExist:
            return http.HttpResponseForbidden('电影不存在')
        try:
            collection = Collection.objects.create(
                user=request.user,
                film=film
            )
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden('收藏失败，请重试')
        return http.JsonResponse({'code':200, 'errmsg':'ok'})

    def get(self, request):
        """查询收藏"""
        films = Film.objects.filter(user=request.user)
        film_dict_list = []
        for film in films:
            film_dict = {
                'id': film.id,
                'title': film.title,
                'image': film.image,
                'url': film.url,
            }
            film_dict_list.append(film_dict)
        return http.JsonResponse({'code':0, 'errmsg':'ok',
                                  films: film_dict_list})


class HistoryView(View):
    def post(self, request):
        """保存用户浏览记录"""

        def post(self, request):
            """保存用户浏览记录"""
            # 接收参数
            json_dict = json.loads(request.body.decode())
            film_id = json_dict.get('film_id')

            # 校验参数:
            try:
                Film.objects.get(id=film_id)
            except Film.DoesNotExist:
                return http.HttpResponseForbidden('电影不存在')

            # 保存用户浏览数据
            redis_conn = get_redis_connection('history')
            pl = redis_conn.pipeline()
            user_id = request.user.id

            # 先去重: 这里给 0 代表去除所有的 film_id
            pl.lrem('history_%s' % user_id, 0, film_id)
            # 再存储
            pl.lpush('history_%s' % user_id, film_id)
            # 最后截取: 界面有限, 只保留 5 个
            pl.ltrim('history_%s' % user_id, 0, 4)
            # 执行管道
            pl.execute()

            # 响应结果
            return http.JsonResponse({'code': 200, 'errmsg': 'OK'})

        def get(self, request):
            """获取用户浏览记录"""
            # 获取Redis存储的film_id列表信息
            redis_conn = get_redis_connection('history')
            film_ids = redis_conn.lrange('history_%s' % request.user.id, 0, -1)

            # 根据film_ids列表数据，查询出商品sku信息
            films = []
            for film_id in film_ids:
                film = Film.objects.get(id=film_id)
                films.append({
                    'id': film_id,
                    'title': film.title,
                    'image': film.image,
                    'url': film.url
                })
            return http.JsonResponse({'code': 200, 'errmsg': 'ok',
                                      'films': films})