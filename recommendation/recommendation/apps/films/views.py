from django import http
from django.core.paginator import Paginator
from django.db.backends.base.schema import logger
from django.shortcuts import render

# Create your views here.
from django.views import View

from films.models import FilmCategory, Film


def func(request, order):
    page_num = request.GET.get('page')
    page_size = request.GET.get('page_size')
    try:
        films = Film.objects.filter().order_by(order)[:2]
    except Exception as e:
        logger.error(e)
        return http.HttpResponseForbidden('数据不存在')
    paginator = Paginator(films, page_size)
    try:
        page_films = paginator.page(page_num)
    except Exception as e:
        logger.error(e)
        # 如果page_num不正确，默认给用户404
        return http.HttpResponseNotFound('empty page')
        # 获取列表页总页数
    total_page = paginator.num_pages
    # 定义列表:
    list = []
    # 整理格式:
    for film in page_films:
        list.append({
            'id': film.id,
            'image': film.image,
            'title': film.title,
            'url': film.url
        })
    # 拼接传给前端的数据:
    return http.JsonResponse({'list': list, 'count': total_page})

class CategoryView(View):
    def get(self, request, category_id):
        """电影分类数据"""
        # page_num = request.GET.get('page')
        # page_size = request.GET.get('page_size')
        order = request.GET.get('ordering')
        # 2.判断category_id是否正确
        try:
            category = FilmCategory.objects.get(id=category_id)
        except FilmCategory.DoesNotExist:
            return http.HttpResponseNotFound('FilmCategory 不存在')

        # try:
        #     films = Film.objects.filter(category=category).order_by(order)
        # except Exception as e:
        #     logger.error(e)
        #     return http.HttpResponseForbidden('数据不存在')
        # paginator = Paginator(films, page_size)
        #
        # try:
        #     page_films = paginator.page(page_num)
        # except Exception as e:
        #     logger.error(e)
        #     # 如果page_num不正确，默认给用户404
        #     return http.HttpResponseNotFound('empty page')
        #     # 获取列表页总页数
        # total_page = paginator.num_pages
        #
        # # 定义列表:
        # list = []
        # # 整理格式:
        # for film in page_films:
        #     list.append({
        #         'id': film.id,
        #         'image': film.image,
        #         'title': film.title,
        #         'url': film.url
        #     })
        # # 拼接传给前端的数据:
        # dict = {
        #     'list': list,
        #     'count': total_page
        # }
        # # 把数据变为 json 发送给前端
        # return http.JsonResponse(dict)
        func(request, order=order)


class GradeView(View):
    def get(self, request):
        """豆瓣评分排行榜数据"""
        # page_num = request.GET.get('page')
        # try:
        #     films = Film.objects.filter().order_by('grade')
        # except Exception as e:
        #     logger.error(e)
        #     return http.HttpResponseForbidden('数据不存在')
        # paginator = Paginator(films, 5)
        # try:
        #     page_films = paginator.page(page_num)
        # except Exception as e:
        #     logger.error(e)
        #     # 如果page_num不正确，默认给用户404
        #     return http.HttpResponseNotFound('empty page')
        #     # 获取列表页总页数
        # total_page = paginator.num_pages
        # # 定义列表:
        # list = []
        # # 整理格式:
        # for film in page_films:
        #     list.append({
        #         'id': film.id,
        #         'image': film.image,
        #         'title': film.title,
        #         'url': film.url
        #     })
        # # 拼接传给前端的数据:
        # return http.JsonResponse({'list': list, 'count':total_page})
        func(request, order='-grade')


class HotView(View):
    def get(self, request):
        """热播剧场"""
        func(request, order='-play_times')


class ClassicsView(View):
    def get(self, request):
        """经典-收藏剧场"""
        func(request, order='-collection_num')


class Category(View):
    def get(self, request):
        """电影类别"""
        try:
            categories = FilmCategory.objects.filter()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden('数据不存在')
        list_dict = []
        for category in categories:
            dict_tem = {
                'id':category.id,
                'name':category.name
            }
            list_dict.append(dict_tem)
        return http.JsonResponse(list_dict)