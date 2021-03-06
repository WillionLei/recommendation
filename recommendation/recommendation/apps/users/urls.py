from django.conf.urls import url

from users import views

urlpatterns = [
    # 用户名
    url(r'^usernames/(?P<username>\w{2,8})/count/$', views.UsernameCountView.as_view()),
    # 手机号
    url(r'^mobile/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    # 用户注册
    url(r'^register/$', views.RegisterView.as_view()),
    # 用户登录
    url(r'^login/$',  views.UserLoginView.as_view()),
    # 退出登录
    url(r'^logout/$', views.LogoutView.as_view()),
    # 用户中心
    url(r'^info/$', views.UserInfoView.as_view()),
    # 修改密码
    url(r'^password/$', views.ChangePwdView.as_view()),
    # 生日
    url(r'^birthday/$', views.ChangeBirthday.as_view()),
    # 收藏
    url(r'^collection/$', views.AddCollections.as_view()),
    # 浏览记录
    url(r'^histroies/$', views.HistoryView.as_view()),

]