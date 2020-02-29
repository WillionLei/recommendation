from django.conf.urls import url

from users import views

urlpatterns = [
    #用户名
    url(r'^usernames/(?P<username>\w{2,8})/count/$',views.UsernameCountView.as_view()),

]