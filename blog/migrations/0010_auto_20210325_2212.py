# Generated by Django 3.1.7 on 2021-03-25 14:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0009_auto_20210325_2207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='blog.user', verbose_name='文章作者'),
        ),
    ]