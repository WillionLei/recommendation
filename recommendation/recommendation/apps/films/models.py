from BaseModel.BaseModel import BaseModel
from django.db import models


class FilmCategory(models.Model):
    """电影类别表"""
    name = models.CharField(max_length=50, verbose_name='名称')

    key = models.CharField(max_length=50, verbose_name='类别')

    class Meta:
        db_table = 'tb_film_category'
        verbose_name = '电影类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Film(models.Model):
    """电影表"""
    # 外键, 关联广告类别
    CHARGE_CHOICES = ((0, '免费'), (1, '会员'), (2, '付费'))
    category = models.ForeignKey(FilmCategory, on_delete=models.PROTECT,
                                 verbose_name='类别')
    title = models.CharField(max_length=20, verbose_name='片名')
    url = models.CharField(max_length=300,
                           verbose_name='影视链接')
    image = models.ImageField(null=True,blank=True, verbose_name='图片')
    release_date = models.DateField(max_length=20, verbose_name='上映时间')
    grade = models.DecimalField(decimal_places=1, max_digits=2, verbose_name='评分')
    director = models.CharField(max_length=30, verbose_name='导演', blank=True)
    protagonist = models.CharField(max_length=50, verbose_name='主演', blank=True)
    charge = models.SmallIntegerField(choices=CHARGE_CHOICES, default=0, verbose_name='费用')
    fcomment = models.CharField(max_length=200, null=True, verbose_name='描述信息')
    # recommendation_level = models.ForeignKey(Level, on_delete=models.PROTECT, verbose_name='推荐分级')

    class Meta:
        db_table = 'tb_film'
        verbose_name = '电影'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.category.name + self.title
