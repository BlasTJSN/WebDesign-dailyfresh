from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpRequest
from django.views.generic import View
from django.core.urlresolvers import reverse
import re
from users.models import User
from django.db import IntegrityError
from celery_tasks.tasks import send_active_email
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from itsdangerous import SignatureExpired
from django.contrib.auth import authenticate, login, logout


# Create your views here.

class LoginView(View):
    """登陆"""

    def get(self,request):
        """响应登陆页面"""
        return render(request, "login.html")

    def post(self,request):
        """处理登陆逻辑"""

        # 获取用户名和密码
        user_name = request.POST.get("username")
        password = request.POST.get("pwd")

        # 参数校验
        if not all([user_name, password]):
            return redirect(reverse("users:login"))

        # Django用户认证系统判断是否登陆成功
        user = authenticate(user_name=user_name,password=password)

        # 验证登陆失败
        if user is None:
            # 响应登陆页面，提示用户名或密码错误
            return render(request, "login.html", {"errmsg":"用户名或密码错误"})

        # 验证登陆成功，判断用户是否激活
        if user.is_active is False:
            # 如果不是激活用户
            return render(request, "login.html", {"errmsg":"用户未激活"})

        # 使用django用户认证系统，在session中保存用户登陆状态
        login(request, user)

        # 登陆成功，重定向到主页
        return redirect(reverse("goods:index"))



class ActiveView(View):
    """邮件激活"""
    def get(self,request,token):
        """处理激活请求"""

        # 创建序列化器
        serializer = Serializer(settings.SECRET_KEY, 3600)

        # 使用序列化器将token还原
        try:
            # 使用序列化器，获取token明文信息，需要判断签名是否过期
            result = serializer.loads(token)

        except SignatureExpired:
            # 提示激活链接已过期
            return HttpResponse("激活链接已过期")

        # 获取用户id
        user_id = result.get("confirm")

        # 通过用户id查询需要激活的用户，需要判断查询的用户是否存在
        try:
            user = User.objects.get(id=user_id)

        except User.DoesNotExist:
            # 提示用户不存在
            return HttpResponse("用户不存在")

        # 设置激活用户的is_active为True
        user.is_active = True

        # 保存数据到数据库
        user.save()

        # 响应信息给客户端：跳转到登陆页面
        return  redirect(reverse("user:login"))


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

        # 生成激活token
        token = user.generate_active_token()

        # celery发送激活邮件：异步完成，发送邮件不会阻塞结果的返回
        send_active_email.delay(email, user_name, token)

        # 返回结果：重定向的首页
        return redirect(reverse('goods:index'))