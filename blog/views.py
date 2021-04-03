from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils import timezone
from django.db.utils import DataError
from django.urls import reverse
from django.contrib.auth import hashers
from django.core import mail
from django.db.models import Q
from . import models
import random
import string
import datetime
import markdown
import random
from django.conf import settings
import sys
# Create your views here.
def get_request_ip(request):
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]  # 所以这里是真实的ip
        else:
            ip = request.META.get('REMOTE_ADDR')  # 这里获得代理ip
    except:
        ip = '错误'

    return ip

def log_the_session(request):
    session_log=models.SessionLog()
    print("DEBUG",request.build_absolute_uri())

    ip=get_request_ip(request)
    server_name = request.build_absolute_uri()
    username=request.session.get('username')

    if username == None:
        username="未登录"
    session_log.username=username
    session_log.server_name=server_name
    session_log.ip=ip
    session_log.save()

def session_logger(func):
    # 记录访问每个视图的用户名，URL，IP
    def wrapper(*args, **kw):
        # FOR DEBUG
        print("args:", args)
        print("kw:", kw)
        request = args[0]
        log_the_session(request)
        return func(*args, **kw)
    return wrapper




def check_logged_in(func):
    # 检查用户是否登录了
    def wrapper(*args, **kw):
        # FOR DEBUG
        print("args:", args)
        print("kw:", kw)
        request = args[0]
        if 'username' not in request.session:
            #           context = {'the_url': reverse('blog:index'),
            #                      'hint': '你还没登录',
            #                      'page': '主页',
            #                  ***REMOVED***
            #           return render(request, 'blog/hint.html', context)
            return hint_and_redirect(request, reverse('blog:index'), '你还没登录,正在返回主页')
        return func(*args, **kw)
    return wrapper


def send_verify_code(request, to_email):
    # 因为是发验证码，所以要有一个过期时间，这里设为5min后过期
    # 如果使用普通的个人邮箱，会有每日发送限制和被锁定的可能
    print("DEBUG MAIL",to_email)
    request.session.set_expiry(60*5)
    verify_code = random.randint(100000, 999999)
    request.session['verify_code'] = str(verify_code)
    msg = '您的验证码为 '+str(verify_code)+' ，请在三分钟内输入'
    mail.send_mail('您的验证码', msg, settings.EMAIL_HOST_USER, [to_email])

@session_logger
def guide_bulletin(request):
    # 硬编码一篇文章，指定为网站公告
    return article_detail(request,15)

def hint_and_redirect(request, the_url, hint, show_hint=True, delay_time=1000):
    if show_hint == False:
        return redirect(the_url)
    else:
        context = {'the_url': the_url,
                   'hint': hint,
                   'delay_time': delay_time,
               ***REMOVED***
        return render(request, 'blog/hint.html', context)


@session_logger
def index(request):
    if 'search_text' in request.GET and request.GET.get('search_text').split() != []:
        search_text = request.GET.get('search_text')
        articles = models.Article.objects.filter(Q(title__icontains=search_text) | Q(
            body__icontains=search_text)).filter(visible=True)

        context = {'articles': articles,
                   'searched': 'yes'
               ***REMOVED***
    else:
        articles = models.Article.objects.order_by('-id').filter(visible=True)
        print(articles)
        context = {'articles': articles,
                   'searched': 'no'
               ***REMOVED***
    # 截取文章开头一部分作为预览
    for a in context['articles']:
        a.body = a.body[:200]
        if len(a.body) == 100:
            a.body += '...'

    return render(request, 'blog/index.html', context)


@session_logger
def article_detail(request, article_id):

    article = get_object_or_404(models.Article, id=article_id)
    try:
        comments= models.Comment.objects.filter(article=article)
        print("DEBUG",comments)
    except models.Comment.DoesNotExist:
        comments=None
    if article.visible == False and 'username' not in request.session:
        raise Http404()
    article.body = markdown.markdown(article.body,
                                     extensions=[
                                         # 包含 缩写、表格等常用扩展
                                         'markdown.extensions.extra',
                                         # 语法高亮扩展
                                         'markdown.extensions.codehilite',
                                     ])
    if comments != None:
        for c in comments:
            c.body = markdown.markdown(c.body,
                                             extensions=[
                                                 # 包含 缩写、表格等常用扩展
                                                 'markdown.extensions.extra',
                                                 # 语法高亮扩展
                                                 'markdown.extensions.codehilite',
                                             ])

    context = {'article': article,
            'comments':comments***REMOVED***
    return render(request, 'blog/article_detail.html', context)


@session_logger
@check_logged_in
def post_comment(request, article_id):

    if request.method == 'POST':
        article = get_object_or_404(models.Article, id=article_id)
        user = get_object_or_404(models.User, id=request.session.get('id'))
        body = request.POST.get('body')
        if body.split() == []:
            return hint_and_redirect(request, reverse('blog:article_detail',args=[article_id]), '评论不能为空')

        new_comment = models.Comment()
        new_comment.article = article
        new_comment.user = user
        new_comment.body = body

        try:
            new_comment.save()
            return hint_and_redirect(request, reverse('blog:article_detail', args=[article_id]), '评论成功',False)
        except DataError:
            return hint_and_redirect(request, reverse('blog:article_detail', args=[article_id]), '数据错误，请检查内容重新发送')
        except:
            return hint_and_redirect(request, reverse('blog:article_detail', args=[article_id]), '未知错误')

    # 处理错误请求
    else:
        return hint_and_redirect(request, reverse('blog:article_detail', args=[article_id]), '评论只支持POST形式发送')


@session_logger
@check_logged_in
def delete_comment(request,comment_id):
    # 之所以用GET方法，完全是因为在前端方便写
    if request.method == 'GET':
        print('收到了get方法')
        print(request.GET.get('delete_comment'))
        if request.GET.get('delete_comment') == 'yes':
            print('DEBUG')
            comment=get_object_or_404(models.Comment,id=comment_id)
            article_id=comment.article.id
            if request.session.get('id') == comment.user.id:
                print("DEBUG session id 和 comment user id 一样")
                comment.delete()
                return hint_and_redirect(request, reverse('blog:article_detail', args=[article_id]), '删除评论成功')
            else:
                return hint_and_redirect(request, reverse('blog:article_detail', args=[article_id]), '您不是评论用户本人，删除评论失败')



@session_logger
def profile(request, username):
    user = get_object_or_404(models.User, username=username)
    user.status = models.User.StatusList(user.status).label
    articles = models.Article.objects.filter(
        author__username=username)

    # 本人登录后浏览个人主页
    if request.session.get('id') == user.id:
        # 为了方便，将状态值的人类可读名称直接赋值给status，方便前台调用
        context = {'articles': articles,
                   'user': user,
                   'is_self': 'yes',
               ***REMOVED***
        return render(request, 'blog/profile.html', context)
    else:
        context = {'articles': articles,
                   'user': user,
                   'is_self': 'no',
               ***REMOVED***
        return render(request, 'blog/profile.html', context)


@session_logger
@check_logged_in
def edit_profile(request):
    try:
        user = models.User.objects.get(id=request.session.get('id'))
    except models.User.DoesNotExist:
        #       context = {'the_url': reverse('blog:index'),
        #                  'hint': '未知错误,可能会话已过期，请尝试重新登录',
        #                  'page': '主页',
        #              ***REMOVED***
        #       return render(request, 'blog/hint.html', context)
        return hint_and_redirect(request, reverse('blog:index'), '未知错误，可能会话已过期，请尝试重新登录')
    if request.method == 'GET':
        context = {'user': user,
               ***REMOVED***
        return render(request, 'blog/edit_profile.html', context)
    elif request.method == 'POST':

        current_username = request.session.get('username')
        username = request.POST.get('username')
        email = request.POST.get('email')
        signature = request.POST.get('signature')
        # 下面的try块代码可能看着很乱，其实很简单，就是如果未改名,
        # 则会执行finally块内容，也就是成功保存。若是改名了，这会
        # 查找是否有同名用户，有的话就会直接return提示信息到前端，
        # 若是无同名用户，则会抛出找不到用户的异常，然后被捕获异常
        # 然后执行finally块内容
        try:
            # 检测数据库中是否已存在同名用户，若抛出该用户
            # 名不存在异常，则为可以存入数据库
            if current_username != username:
                models.User.objects.get(username=username)
                context = {'err_msg': '此用户名已存在，请更换一个',
                           'user': user,
                       ***REMOVED***
                return render(request, 'blog/edit_profile.html', context)
        except models.User.DoesNotExist:
            pass
        finally:
            user.username = username
            user.email = email
            user.signature = signature

        try:
            user.save()
            # 修改成功
#           context = {'the_url': reverse('blog:profile'),
#                      'hint': '修改个人资料成功了',
#                      'page': '个人中心',
#                  ***REMOVED***
#           return render(request, 'blog/hint.html', context)
            request.session['username'] = user.username
            return hint_and_redirect(request, reverse('blog:profile', args=[request.session.get('username')]), '修改个人资料成功', False)
        except DataError:
            context = {'err_msg': '数据错误，请检查您输入的内容是否符合格式',
                   ***REMOVED***
            return render(request, 'blog/register.html', context)
        except:
            return hint_and_redirect(request, reverse('blog:edit_profile'), '未知错误')


@session_logger
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
        new_article.author = models.User.objects.get(id=request.session['id'])
        new_article.codehilite_style = request.POST.get('codehilite_style')
        title = request.POST.get('title')
        body = request.POST.get('body')

        if title.split() == [] or body.split() == []:
           # context = {'the_url': reverse('blog:create_article'),
           #           'hint': '文章主体或标题不能为空',
           #           'page': '写文章界面',
           #       ***REMOVED***
           # return render(request, 'blog/hint.html', context)
            return hint_and_redirect(request, reverse('blog:create_article'), '文章主体或标题不能为空')
        else:
            new_article.title = title
            new_article.body = body
            new_article.save()
           # context = {'the_url': reverse('blog:index'),
           #           'hint': '文章创建成功',
           #           'page': '主页',
           #       ***REMOVED***
           # return render(request, 'blog/hint.html', context)
            return hint_and_redirect(request, reverse('blog:index'), '文章创建成功')


@session_logger
@check_logged_in
def update_article(request, article_id):
    article = models.Article.objects.get(id=article_id)
    if article.author != models.User.objects.get(id=request.session['id']):
        # 理论上，前端早已禁止这种情况发生
       # context = {'the_url': reverse('blog:index'),
       #           'hint': '你不是这篇文章的作者',
       #           'page': '主页',
       #       ***REMOVED***
       # return render(request, 'blog/hint.html', context)
        return hint_and_redirect(request, reverse('blog:index'), '你不是这篇文章的作者')

    if request.method == 'GET':
        context = {'article': article***REMOVED***
        return render(request, 'blog/update_article.html', context)
    if request.method == 'POST':
        article.codehilite_style = request.POST.get('codehilite_style')
        title = request.POST.get('title')
        body = request.POST.get('body')
        if title.split() == [] or body.split() == []:
           # context = {'the_url': reverse('blog:update_article'),
           #           'hint': '文章主体或标题不能为空',
           #           'page': '修改文章界面',
           #       ***REMOVED***
           # return render(request, 'blog/hint.html', context)
            return hint_and_redirect(request, reverse('blog:update_article'), '文章主体或标题不能为空')

        else:
            article.title = title
            article.body = body
            article.save()
           # context = {'the_url': reverse('blog:index'),
           #           'hint': '文章修改成功',
           #           'page': '主页',
           #       ***REMOVED***
           # return render(request, 'blog/hint.html', context)
            return hint_and_redirect(request, reverse('blog:article_detail', args=[article_id]), '文章修改成功', False)


@session_logger
@check_logged_in
def delete_article(request, article_id):
    article = models.Article.objects.get(id=article_id)
    if article.author != models.User.objects.get(id=request.session['id']):
        # 理论上，前端早已禁止这种情况发生
       # context = {'the_url': reverse('blog:index'),
       #           'hint': '你不是这篇文章的作者',
       #           'page': '主页',
       #       ***REMOVED***
       # return render(request, 'blog/hint.html', context)
        return hint_and_redirect(request, reverse('blog:index'), '你不是这篇文章的作者')

    if request.method == 'GET':
        context = {'question': '确认删除吗？'***REMOVED***
        return render(request, 'blog/confirm.html', context)
    if request.method == 'POST':
        if request.POST.get('confirm') == 'yes':
            article.delete()
           # context = {'the_url': reverse('blog:index'),
           #           'hint': '文章删除成功',
           #           'page': '主页',
           #       ***REMOVED***
           # return render(request, 'blog/hint.html', context)
            return hint_and_redirect(request, reverse('blog:index'), '文章删除成功')

        else:
           # context = {'the_url': reverse('blog:index'),
           #           'hint': '文章删除放弃',
           #           'page': '主页',
           #       ***REMOVED***
           # return render(request, 'blog/hint.html', context)
            return hint_and_redirect(request, reverse('blog:article_detail', args=[article_id]), '文章删除放弃')


@session_logger
def reset_password(request):
    if request.method == 'GET':
        # 是否发送了验证码
        request.session['sent'] = 'no'
        context = {'err_msg': '',
                   'sent': 'no',
               ***REMOVED***
        return render(request, 'blog/reset_password.html', context)
    elif request.method == 'POST':
        # print("会话项目",request.session.items())
        # print("会话过期秒数",request.session.get_expiry_age())
        # print("会话到期时间",request.session.get_expiry_date())
        email = request.POST.get('email')
        # 获取当前用户对象
        try:
            user = models.User.objects.get(email=email)
        except models.User.DoesNotExist:
            context = {'err_msg': '此用户不存在',
                       'sent': 'no',
                   ***REMOVED***
            return render(request, 'blog/reset_password.html', context)

        p1 = request.POST.get('password1')
        p2 = request.POST.get('password2')
        if request.session.get('sent') == 'no':
            send_verify_code(request, email)

            try:
                send_verify_code(request, email)
            except:
                request.session['sent'] = 'no'
                context = {'err_msg': '验证码的发送出现了问题，这可能在短时间内无法解决，请改日再来',
                           'sent': 'no',
                       ***REMOVED***
                return render(request, 'blog/reset_password.html', context)

            context = {'email': email,
                       'password1': p1,
                       'password2': p2,
                       'sent': 'yes'
                   ***REMOVED***
            request.session['sent'] = 'yes'
            return render(request, 'blog/reset_password.html', context)
        if request.session.get('sent') == 'yes':
            if request.session.get('verify_code') != request.POST.get('verify_code'):
                context = {'err_msg': '验证码输入错误',
                           'email': email,
                           'password1': p1,
                           'password2': p2,
                           'sent': 'yes',
                       ***REMOVED***
                return render(request, 'blog/reset_password.html', context)
        if request.session.get('sent') == None:
            context = {'err_msg': '验证码过期，请重新获取',
                       'sent': 'no',
                   ***REMOVED***
            return render(request, 'blog/reset_password.html', context)
        if request.session.get('verify_code') == request.POST.get('verify_code'):
            print("验证码对了")

        print(user)
        p1 = request.POST.get('password1')
        p2 = request.POST.get('password2')
        if p1 != p2:
            context = {'err_msg': '两次输入的密码不同，请检查是否有误',
                   ***REMOVED***
            return render(request, 'blog/reset_password.html', context)
        else:
            p1_encrypted = hashers.make_password(p1, None, 'pbkdf2_sha256')
            user.password = p1_encrypted
            try:
                user.save()
                # 注册成功
               # context = {'the_url': reverse('blog:index'),
               #           'hint': '注册成功了',
               #           'page': '主页',
               #       ***REMOVED***
               # return render(request, 'blog/hint.html', context)
                return hint_and_redirect(request, reverse('blog:profile', args=[request.session.get('username')]), '修改密码成功了，正在返回个人中心')

            except DataError:
                context = {'err_msg': '数据错误，请检查您输入的内容是否符合格式',
                       ***REMOVED***
                return render(request, 'blog/reset_password.html', context)
            except:
                return HttpResponse("出BUG了")


@session_logger
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
        # print("会话项目",request.session.items())
        # print("会话过期秒数",request.session.get_expiry_age())
        # print("会话到期时间",request.session.get_expiry_date())
        username = request.POST.get('username')
        email = request.POST.get('email')
        p1 = request.POST.get('password1')
        p2 = request.POST.get('password2')
        if request.session.get('sent') == 'no':
            # 这里由于偷懒，并没有记录是否发送成功了
            try:
                send_verify_code(request, email)
            except Exception as e:
                print(e)
                print(sys.exc_info())
                request.session['sent'] = 'no'
                context = {'err_msg': '验证码的发送出现了问题，这可能在短时间内无法解决，请改日再来',
                           'sent': 'no',
                       ***REMOVED***
                return render(request, 'blog/register.html', context)

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
        if request.session.get('sent') == None:
            context = {'err_msg': '验证码过期，请重新获取',
                       'sent': 'no',
                   ***REMOVED***
            return render(request, 'blog/register.html', context)

        new_user = models.User()
        username = request.POST.get('username')
        # 邮箱也要检测是否唯一
        email = request.POST.get('email')
        p1 = request.POST.get('password1')
        p2 = request.POST.get('password2')

        try:
            # 检测数据库中是否已存在同名用户，若抛出该用户
            # 名不存在异常，则为可以存入数据库
            models.User.objects.get(username=username)
            context = {'err_msg': '此用户名已存在，请更换一个',
                   ***REMOVED***
            return render(request, 'blog/register.html', context)
        except models.User.DoesNotExist:
            new_user.username = username

        try:
            # 检测数据库中是否已存在相同邮箱，若抛出该邮箱
            # 不存在异常，则为可以存入数据库
            models.User.objects.get(email=email)
            context = {'err_msg': '此邮箱已存在，请更换一个',
                   ***REMOVED***
            return render(request, 'blog/register.html', context)
        except models.User.DoesNotExist:
            new_user.email = email

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
               # context = {'the_url': reverse('blog:index'),
               #           'hint': '注册成功了',
               #           'page': '主页',
               #       ***REMOVED***
               # return render(request, 'blog/hint.html', context)
                return hint_and_redirect(request, reverse('blog:index'), '注册成功了')

            except DataError:
                context = {'err_msg': '数据错误，请检查您输入的内容是否符合格式',
                       ***REMOVED***
                return render(request, 'blog/register.html', context)
            except:
                return HttpResponse("出BUG了")


@session_logger
def login(request):
    # 登录页面

    if request.method == 'GET':
        context = {***REMOVED***
        return render(request, 'blog/login.html', context)
    elif request.method == 'POST':
        email = request.POST.get('email')
        p1 = request.POST.get('password1')

        try:
            result = models.User.objects.get(email=email)
            if result.status != models.User.StatusList.ACTIVITY:
               # context = {'the_url': reverse('blog:index'),
               #           'hint': '登录不成功,因为您被封禁',
               #           'page': '主页',
               #       ***REMOVED***
               # return render(request, 'blog/hint.html', context)
                return hint_and_redirect(request, reverse('blog:index'), '登录不成功,因为您被封禁')

            if hashers.check_password(p1, result.password):
                request.session['username'] = result.username
                request.session['id'] = result.id
                # 登录成功
               # context = {'the_url': reverse('blog:index'),
               #           'hint': '登录成功了',
               #           'page': '主页',
               #       ***REMOVED***
               # return render(request, 'blog/hint.html', context)
                return hint_and_redirect(request, reverse('blog:index'), '登录成功了', False)

            else:
                context = {'err_msg': '密码错误',
                       ***REMOVED***
                return render(request, 'blog/login.html', context)

        except models.User.DoesNotExist:
            context = {'err_msg': '此用户不存在',
                   ***REMOVED***
            return render(request, 'blog/login.html', context)
        except:
            return HttpResponse("出BUG了")
    else:
        return HttpResponse("出BUG了")


@session_logger
def logout(request):
    # 读者登出
    if 'username' in request.session:
        print('删掉了session')
        request.session.flush()
   # context = {'the_url': reverse('blog:index'),
   #           'hint': '登出成功了',
   #           'page': '首页',
   #       ***REMOVED***
   # return render(request, 'blog/hint.html', context)
    return hint_and_redirect(request, reverse('blog:index'), '登出成功了', False)

