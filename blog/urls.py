# -*-coding:utf-8-*-
from django.urls import path

from . import views

app_name= 'blog'
urlpatterns = [
        path('hello_world',views.hello_world,name='hello_world'),
        path('',views.index,name='index'),
        path('register',views.register,name='register'),
        path('login',views.login,name='login'),
        path('logout',views.logout,name='logout'),
        path('article_detail/<int:id>',views.article_detail,name='article_detail'),
        path('create_article',views.create_article,name='create_article'),
        ]
