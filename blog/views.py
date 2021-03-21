from django.shortcuts import render
from django.shortcuts import get_object_or_404,get_list_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.utils import timezone
from django.db.utils import DataError
from django.urls import reverse
from django.contrib.auth import hashers
from . import models
import random
import string
import datetime

# Create your views here.

def hello_world(request):
    return HttpResponse("你好，世界")
def index(request):
    return HttpResponse("主页测试")
