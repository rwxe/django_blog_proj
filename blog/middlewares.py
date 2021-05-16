from django.utils.deprecation import MiddlewareMixin
from . import models
import urllib

class SessionLogger:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def get_request_ip(self,request):
        try:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]  # 所以这里是真实的ip
            else:
                ip = request.META.get('REMOTE_ADDR')  # 这里获得代理ip
        except:
            ip = '错误'

        return ip

    def log_the_session(self,request):
        session_log=models.SessionLog()
        print("DEBUG",request.build_absolute_uri())

        ip=self.get_request_ip(request)
        server_name = request.build_absolute_uri()
        # 将编码后的中文解码回中文
        server_name = urllib.parse.unquote(server_name)
        if len(server_name)>100:
            #超过一定长度的地址截断，然后加上省略号
            server_name=server_name[:97]+'...'
        username=request.session.get('username')

        if username == None:
            username="未登录"
        session_log.username=username
        session_log.server_name=server_name
        session_log.ip=ip
        session_log.save()

    def session_logger(self,func):
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
        print("中间件  process_view 生效")
        print('view_func 是',view_func)
        self.log_the_session(request)
        pass
