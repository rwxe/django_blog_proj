# 一个普通的 Django 博客项目

一个普通的 Django 博客，或是论坛。之所以有论坛的属性，是因为在开发中，加入了用户注册和发文的功能，当然网站的搭建者可以选择注释掉这些功能。  
目前已经有了博客的主要功能：注册、登录、发文、评论、搜索文章。管理员可通过 Django 自带的管理页面对文章、用户进行管理。  

## 内容列表

之后再写目录  

## 背景

这是一个本人为了学习和练习 Django 框架所写出的项目，项目开发时使用的 Django 版本为3.1，Python 版本为3.8.6 。项目中功能的实现方式未必是最优秀的，主要用以供大家参考学习。  

## 安装

首先克隆此仓库到本地  
```sh
git clone git@github.com:yizdu/django_blog_proj.git
```

### 创建配置文件

在仓库的`proj`目录下，也就是和`settings.py`文件同级目录下新建文件`project_config.py`，里面写入 Django 的数据库配置和邮件服务器配置。数据库配置这里以 MySQL 来做示例，你也可以参考的 Django 的[官方文档](https://docs.djangoproject.com/zh-hans/3.2/ref/settings/#databases)配置使用其他数据库。邮件服务器的配置，需要获取你的邮件服务商STMP服务器地址和端口等信息，具体需要填入的信息，需要你咨询你所使用的邮件服务商（比如QQ邮箱、163邮箱等）。  
```py
# -*-coding:utf-8-*-

#project_config.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # 选择 MySQL 作为数据库管理系统
        'NAME': '', # 你的数据库名称
        'USER': '', # 你的数据库用户名
        'PASSWORD': '', # 你的数据库密码
        'HOST': '127.0.0.1', # 数据库的地址，在本机就写127.0.0.1
        'PORT': '3306', # MySQL 的默认端口
        'TEST':{ 'NAME':''} # 测试数据库名称，Django 运行测试时将创建以此为名的临时数据库
    }
}
EMAIL_HOST = '' # 你的邮箱SMTP服务器地址
EMAIL_PORT = 0 # SMTP服务的端口号
EMAIL_HOST_USER = '' #你的邮箱，也就是邮件发送者的邮箱
EMAIL_HOST_PASSWORD = '' #你邮箱的密码
EMAIL_USE_TLS = True #与SMTP服务器通信时,是否启用TLS（安全）连接

```

### 安装依赖

安装`mysqlclient`  
以 Linux 的 Ubuntu 发行版为示范  
```sh
apt install mysql-client libmysqlclient-dev libssl-dev libcrypto++-dev 
pip install mysqlclient
```
安装其他必要的python包  
```
pip install -r requirements.txt
```

## 使用说明

### 开发环境运行

配置好上述配置文件和依赖后，在`manage.py`当前目录下运行  
```sh
python manage.py runserver
```
然后浏览器访问` http://127.0.0.1:8000`即可看见项目界面  

若希望在同一局域网内被其他主机访问，需要确保`settings.py`内有如下设置  
```
ALLOWED_HOSTS = ['*']
```
然后运行  
```sh
python manage.py runserver 0.0.0.0:80
```

若是希望不让用户看见DEBUG信息，则需在`settings.py`内设置  
```py
DEBUG = False
ALLOWED_HOSTS = ['*']
```

然后运行  
```sh
python manage.py runserver 0.0.0.0:80 --insecure
```

### 生产环境部署

这里以 Linux 的 Ubuntu 发行版为示范，使用nginx + uwsgi + django + linux 的架构部署该项目  
具体可参考uwsgi的官方[指导文档](https://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html#setting-up-django-and-your-web-server-with-uwsgi-and-nginx)

## 致谢

本项目参考了[ stacklens/django_blog_tutorial ](https://github.com/stacklens/django_blog_tutorial)


## 使用许可

[MPL 2.0](LICENSE)
