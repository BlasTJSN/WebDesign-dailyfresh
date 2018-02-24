from django.shortcuts import render
from django.http import HttpResponse,HttpRequest
from django.views.generic import View
# Create your views here.

# 类视图的使用
class RegisterView(View):
    """类视图：处理注册"""

    def get(self,requset):
        """处理GET请求，返回注册页面"""
        return render(requset,"register.html")

    def post(self,request):
        """处理POST请求，实现注册逻辑"""
        return HttpResponse("这里实现注册逻辑")