from django.conf.urls import url

from films import views

urlpatterns = [
    # 分类-电影
    url(r'^list/(?P<category_id>\d+)/films/$', views.CategoryView.as_view()),
    # 好评榜
    url(r'^grade/$', views.GradeView.as_view()),
    # 热播剧场
    url(r'^hot/$', views.HotView.as_view()),
    # 经典剧场
    url(r'^classics/$', views.ClassicsView.as_view()),
    # 分类-类别
    url(r'^category/$', views.Category.as_view()),

]