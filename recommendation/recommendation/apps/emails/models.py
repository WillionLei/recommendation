from django.conf import settings

from itsdangerous import TimedJSONWebSignatureSerializer


def generate_veify_email(self):
    """
    生成邮箱验证链接
    :param self: 当前登录用户
    :return: verify_url
    """
    # 调用itsdangerous中的类，生成对象，有限期：5分钟
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,
                                                expires_in=60*5)

    data = {'user_id': self.id, 'email': self.email}
    # 生成token，byte类型 解码为 str:
    token = serializer.dumps(data).decode()
    verify_url = settings.EMAIL_VERIFY_URL + token
    return verify_url