import re

from django.contrib.auth.backends import ModelBackend

from users.models import User


def get_use_by_account(mobile):
    """判断mobile是否是手机号码"""
    try:
        if re.match('^1[3-9]\d{9}$', mobile):
            user = User.objects.get(mobile=mobile)
        else:
            user = User.objects.get(username=mobile)
    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """自定义用户认证"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_use_by_account(username)
        if user and user.check_password(password):
            return user
