# -*-coding:utf-8-*-
from django.urls import path

from . import views

app_name= 'blog'
urlpatterns = [
        path('guide_bulletin',views.guide_bulletin,name='guide_bulletin'),
        path('',views.index,name='index'),
        path('register',views.register,name='register'),
        path('login',views.login,name='login'),
        path('logout',views.logout,name='logout'),
        path('article_detail/<int:article_id>',views.article_detail,name='article_detail'),
        path('post_comment/<int:article_id>',views.post_comment,name='post_comment'),
        path('delete_comment/<int:comment_id>',views.delete_comment,name='delete_comment'),
        path('create_article',views.create_article,name='create_article'),
        path('update_article/<int:article_id>',views.update_article,name='update_article'),
        path('delete_article/<int:article_id>',views.delete_article,name='delete_article'),
        path('profile/<str:username>',views.profile,name='profile'),
        path('edit_profile',views.edit_profile,name='edit_profile'),
        path('reset_password',views.reset_password,name='reset_password'),
        ]
