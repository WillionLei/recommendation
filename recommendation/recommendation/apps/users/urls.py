from django.conf.urls import url

from users import views

urlpatterns = [
    # 用户名
    url(r'^usernames/(?P<username>\w{2,8})/count/$', views.UsernameCountView.as_view()),
    # 手机号
    url(r'^mobile/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    # 用户注册
    url(r'^register/$', views.RegisterView.as_view()),
]