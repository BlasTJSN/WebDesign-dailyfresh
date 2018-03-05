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
from utils.views import LoginRequiredMixin
from users.models import Address
from django_redis import get_redis_connection
from goods.models import GoodsSKU
import json



# Create your views here.

class UserInfoView(LoginRequiredMixin, View):
    """个人信息"""

    def get(self, request):
        """查询个人基本信息和最近的浏览记录，并渲染模板"""

        user = request.user
        try:
            address = user.address_set.latest("create_time")
        except Address.DoesNotExist:
            address = None


        # 查询浏览记录，从redis中查询处浏览记录信息，以history_userid的形式存储在redis中
        # 创建redis连接对象
        redis_conn = get_redis_connection("default")
        # 查询出需要展示的浏览记录数据,前五个数据
        sku_ids = redis_conn.lrange("history_%s" % user.id, 0, 4)
        # 记录sku模型对象的列表
        sku_list = []
        # 遍历sku_ids,取出sku_id
        for sku_id in sku_ids:
            # 使用sku_id查询GoodsSKU
            sku = GoodsSKU.objects.get(id=sku_id)
            sku_list.append(sku)
        # 因为从redis中取数据的顺序和存数据相反，所以要新建一个列表把取出的数据添加进去，保证与存入的顺序即浏览顺序一致


        context = {
            "address":address,
            "sku_list":sku_list
        }

        return render(request,"user_center_info.html", context)




class AddressView(LoginRequiredMixin,View):
    """收货地址"""

    def get(selfself,request):
        """提供用户地址页面:如果验证失败重定向到登陆页面"""

        # 从request中获取user对象,Django用户认证系统中间件中，会在请求中验证用户，用户登陆了，request就会获得user对象
        user = request.user

        try:
            # 查询用户地址：根据创建时间排序，最近的时间在最前，取第1个地址
            # user对象在过滤器中默认等于它的主键，即id
            # address = Address.object.filter(user=user).order_by("-create_time")[0]
            # user和address是一对多的关系，可以使用基础管理查询
            # address = user.address_set.order_by("-create_time")[0]
            # 使用latest("时间")函数,按时间排序，默认倒序,取第一个值
            address = user.address_set.latest("create_time")
        except Address.DoesNotExit:
            # 如果地址信息不存在
            address = None

        # 构造上下文
        context = {
                "address":address
            }
        return render(request, "user_center_site.html", context)

    def post(self,request):
        """编辑地址"""

        # 接收地址表单数据
        user = request.user
        recv_name = request.POST.get("recv_name")
        addr = request.POST.get("addr")
        zip_code = request.POST.get("zip_code")
        recv_mobile = request.POST.get("recv_mobile")

        # 校验参数，这里只做空校验
        if all([user, recv_name, addr, zip_code, recv_mobile]):
            # 保存地址信息到数据库
            Address.object.create(
                user=user,
                receiver_name=recv_name,
                detail_addr=addr,
                zip_code=zip_code,
                receiver_mobile=recv_mobile
            )
        return redirect(reverse("users:address"))


class LogoutView(View):
    """退出登陆"""

    def get(self,request):
        """处理退出登陆逻辑"""

        # 由Django用户认证系统完成，需要清理cookie和session,request参数中有user对象
        logout(request)

        # 退出后跳转
        return redirect(reverse("user:login"))





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
        # 获取记住用户选项状态
        remembered = request.POST.get("remembered")

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

        # 判断是否勾选"记住用户名"
        if remembered != "on":
            # 没有勾选，不需要记住cookie信息，浏览会话结束后过期，时间设置为0
            request.session.set_expiry(0)
        else:
            # 已购选，需要记住cookie信息,时间设置为None，默认为14天
            request.session.set_expiry(None)

        # 在界面跳转前，将cookie中的购物车数据添加到redis中
        cart_json = request.COOKIES.get("cart")
        if cart_json is not None:
            cart_dict_cookie = json.loads(cart_json)
        else:
            cart_dict_cookie = {}

        # 查询redis中的购物车数据
        redis_conn = get_redis_connection("default")
        cart_dict_redis = redis_conn.hgetall("cart_%s" % user.id)

        # 遍历cookie中的购物车数据
        for sku_id, count in cart_dict_cookie.items():
            # 将string转换成bytes类型
            sku_id = sku_id.encode()
            # 判断cookie中的商品在redis中是否存在
            if sku_id in cart_dict_redis:
                origin_count = cart_dict_redis[sku_id]

                count += int(origin_count)
                # 此处是伪代码;大家需要知道如果登录和未登录进行合并后,会有库存的问题即可
                # sku = GoodsSKU.objects.get(id=sku_id)
                # if count > sku.stock:
                #     return '提示用户'

            # 将cookie中的购物车数据添加到redis中
            cart_dict_redis[sku_id] = count
        if cart_dict_redis:
            redis_conn.hmset("cart_%s" % user.id, cart_dict_redis)


        # next的作用
        # 登陆成功，根据next的参数决定跳转方向
        next = request.GET.get("next")
        if next is None:
            # 如果是直接登陆成功，重定向到首页
            response =  redirect(reverse("goods:index"))
        else:
            if next == "orders/place":
                response = redirect(reverse("cart:info"))
            else:
                # 如果是从限制访问页面重定向到登陆页面的，跳转回限制访问页面
                response =  redirect(next)

        # 清空cookie
        response.delete_cookie("cart")
        return response

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

