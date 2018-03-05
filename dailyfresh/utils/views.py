from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from functools import wraps
from django.db import transaction



class LoginRequiredMixin(object):
    """验证用户是否登陆"""

    @classmethod
    def as_view(cls, **initkwargs):
        """重写父类的as_view()"""

        # 得到类视图调用as_view()后的结果
        view = super().as_view(**initkwargs)

        return login_required(view)

def login_required_json(view_func):
    """验证用户是否登录，并响应json"""

    # 装饰器会修改方法的 __name__,有可能修改类视图中定义的请求方法的名字,造成请求分发失败
    # wraps装饰会保证被装饰的函数的__name__不会被改变.而且会保留原有的说明文档信息
    @wraps(view_func)
    # 参数request是View类封装的方法view中的
    def wrapper(request, *args, **kwargs):
        """判断用户是否登录，如果未登录响应JSON,如果登录进入到视图"""
        if not request.user.is_authenticated():
            return JsonResponse({"code":1, "message":"用户未登录"})
        else:
            # 进入视图就是调用视图，保证视图内部的代码可以被执行
            return view_func(request, *args, **kwargs)
    return wrapper

class LoginRequiredJSONMixin(object):
    """JSON装饰器"""

    @classmethod
    def as_view(cls, *args, **kwargs):
        """使用login_required_jso装饰器，装饰view的as_view()执行后的结果"""
        view = super().as_view(*args, **kwargs)

        return login_required_json(view)


class TransactionAtomicMixin(object):
    """事务装饰器"""

    @classmethod
    def as_view(cls, *args, **kwargs):
        """使用transaction.atomic装饰器，装饰view的as_view()执行后的结果"""
        view = super().as_view(*args, **kwargs)

        return transaction.atomic(view)
