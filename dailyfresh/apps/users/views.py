from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpRequest
from django.views.generic import View
from django.core.urlresolvers import reverse
import re
from users.models import User
from django.db import IntegrityError


# Create your views here.

# 类视图的使用
class RegisterView(View):
    """类视图：处理注册"""

    def get(self,requset):
        """处理GET请求，返回注册页面"""
        return render(requset,"register.html")

    def post(self,request):
        """处理POST请求，实现注册逻辑"""

        # 获取注册请求参数
        user_name = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")
        allow = request.POST.get("allow")

        # 参数校验：缺少任意一个参数，就不要继续执行
        if not all([user_name,password,email]):
            # 如果注册数据不全，重新刷新一下注册页面
            return redirect(reverse("users:register"))
        # 判断邮箱格式
        if not re.match(r"^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email):
            return render(request, 'register.html', {'errmsg':'邮箱格式不正确'})
        # 判断是否勾选协议
        if allow != "on":
            return render(request, "register.html", {"errmsg":"没有勾选用户协议"})
        # Django用户认证系统，保存用户注册数据到数据库:不需要调用save()
        try:
            user = User.objects.create_user(user_name, email, password)
        except IntegrityError:
            # 判断注册用户重名
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 手动将用户认证系统默认的激活状态设置成False,默认是True
        user.is_active = False
        # 保存数据到数据库
        user.save()


        return HttpResponse("这里实现注册逻辑")