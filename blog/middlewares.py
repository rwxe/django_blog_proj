from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from . import models
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
import urllib


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


class SessionLogger:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        # 记录所有请求的ip
        self.log_the_session(request)

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def log_the_session(self, request):
        session_log = models.SessionLog()
        print("DEBUG", request.build_absolute_uri())

        ip = get_request_ip(request)
        server_name = request.build_absolute_uri()
        # 将编码后的中文解码回中文
        server_name = urllib.parse.unquote(server_name)
        if len(server_name) > 100:
            # 超过一定长度的地址截断，然后加上省略号
            server_name = server_name[:97]+'...'
        username = request.session.get('username')

        if username == None:
            username = "未登录"
        session_log.username = username
        session_log.server_name = server_name
        session_log.ip = ip
        session_log.save()

    def session_logger(self, func):
        # 记录访问每个视图的用户名，URL，IP
        def wrapper(*args, **kw):
            # FOR DEBUG
            print("args:", args)
            print("kw:", kw)
            request = args[0]
            log_the_session(request)
            return func(*args, **kw)
        return wrapper

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass


class VisitLimit:

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # 检查所有的请求是否过于频繁
        ip = get_request_ip(request)
        ip_count = cache.get(ip, 0)

        if ip_count > 0:
            cache.incr(ip)
        else:
            cache.set(ip, 1, timeout=60)
        if ip_count >= settings.IP_QPM:
            return HttpResponse("请求过于频繁，请稍候再尝试")

        response = self.get_response(request)

        return response
