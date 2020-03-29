from django.db import models

# Create your models here.


class Level(models.Model):
    name = models.CharField(max_length=10, verbose_name='权限')

    class Meta:
        db_table = 'tb_level'
        verbose_name = '权限'
        verbose_name_plural = verbose_name