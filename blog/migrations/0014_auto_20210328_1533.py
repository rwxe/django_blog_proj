# Generated by Django 3.1.7 on 2021-03-28 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0013_auto_20210328_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='status',
            field=models.CharField(choices=[('A', '正常'), ('B', '封禁中'), ('C', '已注销')], default='A', max_length=1, verbose_name='状态'),
        ),
    ]