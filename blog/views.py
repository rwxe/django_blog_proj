from django.shortcuts import render
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.db.utils import DataError
from django.urls import reverse
from django.contrib.auth import hashers
from django.core import mail
from . import models
import random
import string
import datetime
import markdown
import random
from django.conf import settings

# Create your views here.


def check_logged_in(func):
    # 检查用户是否登录了
    def wrapper(*args, **kw):
        # FOR DEBUG
        print("args:", args)
        print("kw:", kw)
        request = args[0]
        if 'username' not in request.session:
            context = {'the_url': reverse('blog:index'),
                       'hint': '你还没登录',
                       'page': '主页',
                   ***REMOVED***
            return render(request, 'blog/hint.html', context)
        return func(*args, **kw)
    return wrapper


def send_verify_code(request, to_email):
    # 因为是发验证码，所以要有一个过期时间，这里设为5min后过期
    request.session.set_expiry(60*5)
    verify_code = random.randint(100000, 999999)
    request.session['verify_code'] = str(verify_code)
    msg = '您的验证码为 '+str(verify_code)+' ，请在三分钟内输入'
    mail.send_mail('您的验证码', msg, settings.EMAIL_HOST_USER, [to_email])


def hello_world(request):
    return HttpResponse("你好，世界")


def index(request):
    articles = models.Article.objects.order_by('-id')
    context = {'articles': articles***REMOVED***
#   return HttpResponse("主页测试")
    return render(request, 'blog/index.html', context)


def article_detail(request, id):
    article = models.Article.objects.get(id=id)
    article.body = markdown.markdown(article.body,
                                     extensions=[
                                         # 包含 缩写、表格等常用扩展
                                         'markdown.extensions.extra',
                                         # 语法高亮扩展
                                         'markdown.extensions.codehilite',
                                     ])
    context = {'article': article***REMOVED***
    return render(request, 'blog/article_detail.html', context)


@check_logged_in
def profile(request):
    articles = models.Article.objects.filter(
        author_id=request.session.get('id'))
    user = models.User.objects.get(id=request.session.get('id'))
    # 为了方便，将状态值的人类可读名称直接赋值给status，方便前台调用
    user.status = models.User.StatusList(user.status).label
    context = {'articles': articles,
               'user': user,
           ***REMOVED***
#   return HttpResponse("主页测试")
    return render(request, 'blog/profile.html', context)


@check_logged_in
def create_article(request):
    #   if 'username' not in request.session:
    #       context={'the_url':reverse('blog:index'),
    #               'hint':'你还没登录',
    #               'page':'主页',
    #           ***REMOVED***
    #       return render(request,'blog/hint.html',context)
    if request.method == 'GET':
        return render(request, 'blog/create_article.html')
    if request.method == 'POST':
        new_article = models.Article()
        # 临时设置成id 1
        new_article.author = models.User.objects.get(id=request.session['id'])
        new_article.codehilite_style = request.POST.get('codehilite_style')
        title = request.POST.get('title')
        body = request.POST.get('body')

        if title.split() == [] or body.split() == []:
            context = {'the_url': reverse('blog:create_article'),
                       'hint': '文章主体或标题不能为空',
                       'page': '写文章界面',
                   ***REMOVED***
            return render(request, 'blog/hint.html', context)
        else:
            new_article.title = title
            new_article.body = body
            new_article.save()
            context = {'the_url': reverse('blog:index'),
                       'hint': '文章创建成功',
                       'page': '主页',
                   ***REMOVED***
            return render(request, 'blog/hint.html', context)


@check_logged_in
def update_article(request, id):
    article = models.Article.objects.get(id=id)
    if article.author != models.User.objects.get(id=request.session['id']):
        # 理论上，前端早已禁止这种情况发生
        context = {'the_url': reverse('blog:index'),
                   'hint': '你不是这篇文章的作者',
                   'page': '主页',
               ***REMOVED***
        return render(request, 'blog/hint.html', context)

    if request.method == 'GET':
        context = {'article': article***REMOVED***
        return render(request, 'blog/update_article.html', context)
    if request.method == 'POST':
        article.codehilite_style = request.POST.get('codehilite_style')
        title = request.POST.get('title')
        body = request.POST.get('body')
        if title.split() == [] or body.split() == []:
            context = {'the_url': reverse('blog:update_article'),
                       'hint': '文章主体或标题不能为空',
                       'page': '修改文章界面',
                   ***REMOVED***
            return render(request, 'blog/hint.html', context)
        else:
            article.title = title
            article.body = body
            article.save()
            context = {'the_url': reverse('blog:index'),
                       'hint': '文章修改成功',
                       'page': '主页',
                   ***REMOVED***
            return render(request, 'blog/hint.html', context)


@check_logged_in
def delete_article(request, id):
    article = models.Article.objects.get(id=id)
    if article.author != models.User.objects.get(id=request.session['id']):
        # 理论上，前端早已禁止这种情况发生
        context = {'the_url': reverse('blog:index'),
                   'hint': '你不是这篇文章的作者',
                   'page': '主页',
               ***REMOVED***
        return render(request, 'blog/hint.html', context)

    if request.method == 'GET':
        context = {'article': article***REMOVED***
        return render(request, 'blog/delete_article.html')
    if request.method == 'POST':
        if request.POST.get('confirm') == 'yes':
            article.delete()
            context = {'the_url': reverse('blog:index'),
                       'hint': '文章删除成功',
                       'page': '主页',
                   ***REMOVED***
            return render(request, 'blog/hint.html', context)
        else:
            context = {'the_url': reverse('blog:index'),
                       'hint': '文章删除放弃',
                       'page': '主页',
                   ***REMOVED***
            return render(request, 'blog/hint.html', context)


def register(request):
    # 注册页面
    if request.method == 'GET':
        # 是否发送了验证码
        request.session['sent'] = 'no'
        context = {'err_msg': '',
                   'sent': 'no',
               ***REMOVED***
        return render(request, 'blog/register.html', context)
    elif request.method == 'POST':
        #print("会话项目",request.session.items())
        #print("会话过期秒数",request.session.get_expiry_age())
        #print("会话到期时间",request.session.get_expiry_date())
        username = request.POST.get('username')
        email = request.POST.get('email')
        p1 = request.POST.get('password1')
        p2 = request.POST.get('password2')
        if request.session.get('sent') == 'no':
            send_verify_code(request, email)
            context = {'username': username,
                       'email': email,
                       'password1': p1,
                       'password2': p2,
                       'sent': 'yes'
                   ***REMOVED***
            request.session['sent'] = 'yes'
            return render(request, 'blog/register.html', context)
        if request.session.get('sent') == 'yes':
            if request.session.get('verify_code') != request.POST.get('verify_code'):
                context = {'err_msg': '验证码输入错误',
                           'username': username,
                           'email': email,
                           'password1': p1,
                           'password2': p2,
                           'sent': 'yes',
                       ***REMOVED***
                return render(request, 'blog/register.html', context)
        if request.session.get('sent')==None:
            context = {'err_msg': '验证码过期，请重新获取',
                       'sent': 'no',
                   ***REMOVED***
            return render(request, 'blog/register.html', context)

        new_user = models.User()
        username = request.POST.get('username')
        new_user.email = request.POST.get('email')
        p1 = request.POST.get('password1')
        p2 = request.POST.get('password2')
        try:
            models.User.objects.get(username=username)
            context = {'err_msg': '此用户名已存在，请更换一个',
                   ***REMOVED***
            return render(request, 'blog/register.html', context)
        except models.User.DoesNotExist:
            new_user.username = username
        if p1 != p2:
            context = {'err_msg': '两次输入的密码不同，请检查是否有误',
                   ***REMOVED***
            return render(request, 'blog/register.html', context)
        else:
            p1_encrypted = hashers.make_password(p1, None, 'pbkdf2_sha256')
            new_user.password = p1_encrypted
            try:
                new_user.save()
                # 注册成功
                context = {'the_url': reverse('blog:index'),
                           'hint': '注册成功了',
                           'page': '主页',
                       ***REMOVED***
                return render(request, 'blog/hint.html', context)
            except DataError:
                context = {'err_msg': '数据错误，请检查您输入的内容是否符合格式',
                       ***REMOVED***
                return render(request, 'blog/register.html', context)
            except:
                return HttpResponse("出BUG了")


def login(request):
    # 登录页面

    if request.method == 'GET':
        context = {***REMOVED***
        return render(request, 'blog/login.html', context)
    elif request.method == 'POST':
        username = request.POST.get('username')
        p1 = request.POST.get('password1')

        try:
            result = models.User.objects.get(username=username)
            if result.status != models.User.StatusList.ACTIVITY:
                context = {'the_url': reverse('blog:index'),
                           'hint': '登录不成功,因为您被封禁',
                           'page': '主页',
                       ***REMOVED***
                return render(request, 'blog/hint.html', context)

            if hashers.check_password(p1, result.password):
                request.session['username'] = username
                request.session['id'] = models.User.objects.get(
                    username=username).id
                # 登录成功
                context = {'the_url': reverse('blog:index'),
                           'hint': '登录成功了',
                           'page': '主页',
                       ***REMOVED***
                return render(request, 'blog/hint.html', context)
            else:
                context = {'err_msg': '密码错误',
                       ***REMOVED***
                return render(request, 'blog/login.html', context)

        except models.User.DoesNotExist:
            context = {'err_msg': '此用户名不存在',
                   ***REMOVED***
            return render(request, 'blog/login.html', context)
        except:
            return HttpResponse("出BUG了")
    else:
        return HttpResponse("出BUG了")


def logout(request):
    # 读者登出
    if 'username' in request.session:
        print('删掉了session')
        request.session.flush()
    context = {'the_url': reverse('blog:index'),
               'hint': '登出成功了',
               'page': '首页',
           ***REMOVED***
    return render(request, 'blog/hint.html', context)
