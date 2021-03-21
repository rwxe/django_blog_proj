# -*-coding:utf-8-*-
from django.urls import path

from . import views

app_name= 'blog'
urlpatterns = [
        path('hello_world',views.hello_world,name='hello_world'),
        path('',views.index,name='index'),
        ]
