# Generated by Django 3.1.7 on 2021-03-22 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20210322_2140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='signature',
            field=models.CharField(default='该用户还没有个性签名', max_length=50, verbose_name='个性签名'),
        ),
    ]