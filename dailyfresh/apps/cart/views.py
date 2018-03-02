from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from goods.models import GoodsSKU
from django_redis import get_redis_connection
import re
# Create your views here.

class AddCartView(View):
    """添加购物车"""

    def post(self,request):
        """接收ajax的post发来的购物车数据，存到redis"""

        # 判断用户是否登陆
        if not request.user.is_authenticated():
            return JsonResponse({"code":1, "message":"用户未登录"})

        # 接收购物车数据，user_id, sku_id, count
        user_id = request.user.id
        sku_id = request.POST.get("sku_id")
        count = request.POST.get("count")
        # 校验参数
        if not all([user_id, sku_id, count]):
            return JsonResponse({"code":2, "message":"缺少参数"})

        # 判断商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({"code":3, "message":"sku_id错误"})
        # 判断count是否是整数
        if re.match(r"^\d+$", str(count)):
            count = int(count)
        else:
            return JsonResponse({"code":4, "message": "商品count错误"})

        # 判断库存 sku.stock
        if count > sku.stock:
            return JsonResponse({"code":5, "message":"库存不足"})

        # 加入购物车 保存到redis
        redis_conn = get_redis_connection("default")
        # 判断要添加的数据是否存在，如果存在，累加，不存在，赋值新值
        origin_count = redis_conn.hget("cart_%s" % user_id, sku_id)
        if origin_count:
            count += int(origin_count)

        redis_conn.hset("cart_%s" % user_id, sku_id, count)


        # 为了配合模板中js交互并展示购物车的数量，在这里需要查询一下购物车的总数
        cart_num = 0
        cart_dict = redis_conn.hgetall('cart_%s' % user_id)
        for val in cart_dict.values():
            cart_num += int(val)
        # json方式响应添加购物车结果
        return JsonResponse({"code":0, "message":"添加购物车成功", "cart_num":cart_num})
