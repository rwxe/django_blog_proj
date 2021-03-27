from django.db import models
from django.utils import timezone
# Create your models here.

class User(models.Model):
    # ID自动创建
    # 用户名不可重复
    username = models.CharField(max_length=50, unique=True, verbose_name='用户名')
    signature = models.CharField(max_length=50 ,verbose_name='个性签名',blank=True,default='')
    email = models.CharField(max_length=100, verbose_name='邮箱')
    password = models.CharField(max_length=100, verbose_name='密码字段')
    # 状态有正常'A',封禁'B',已注销'C'
    # 用户注销后，数据库并不会删除此用户，只是将该用户状态修改为'closed'
    class StatusList(models.TextChoices):
            ACTIVITY = 'A', '正常'
            BANNED = 'B', '封禁中'
            CLOSE = 'C', '已注销'
    status = models.CharField(max_length=1, verbose_name='状态',choices=StatusList.choices)

    def __str__(self):
        return self.username


class Article(models.Model):
    # ID自动创建
    # 因为作者不会被删除，所以文章在作者注销账号后，依然会存在于数据库
    author = models.ForeignKey(
        User, on_delete=models.RESTRICT, verbose_name='文章作者')
    title = models.CharField(max_length=100, verbose_name='标题')
    body = models.TextField('正文')
    created = models.DateTimeField(default=timezone.now, verbose_name='创建时间')

    # 文章更新时间。参数 auto_now=True 指定每次数据更新时自动写入当前时间
    updated = models.DateTimeField(auto_now=True,verbose_name='更新时间')

    def __str__(self):
        return self.title

