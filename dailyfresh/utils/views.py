from django.contrib.auth.decorators import login_required

class LoginRequiredMixin(object):
    """验证用户是否登陆"""

    @classmethod
    def as_view(cls, **initkwargs):
        """重写父类的as_view()"""

        # 得到类视图调用as_view()后的结果
        view = super().as_view(**initkwargs)

        return login_required(view)
