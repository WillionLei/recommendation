from django.conf.urls import url

from emails import views

urlpatterns = [
    # 添加邮箱
    url(r'^email/$', views.EmailView.as_view()),
    # 验证邮箱
    url(r'^emails/verification/$', views.VerifyEmailView.as_view())
]