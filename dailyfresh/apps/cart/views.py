from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from goods.models import GoodsSKU
from django_redis import get_redis_connection
import re
import json
# Create your views here.





class CartInfoView(View):
    """展示购物车数据"""

    def get(self, request):
        """查询登陆和未登录的购物车数据，并渲染"""

        if request.user.is_authenticated():
            # 用户已登录，从redis中查询购物车数据
            redis_conn = get_redis_connection("default")
            user_id = request.user.id

            cart_dict = redis_conn.hgetall("cart_%s" % user_id)

        else:
            # 用户未登录，从cookie中查询购物车数据
            cart_json = request.COOKIES.get("cart")
            # json模块读取的cookie中的购物车数据,key是string,而value是int
            if cart_json is not None:
                cart_dict = json.loads(cart_json)
            else:
                cart_dict = {}

        # 定义要展示的变量
        skus = []
        total_count = 0
        total_sku_amount = 0

        # 遍历所有购物车商品信息，查询商品和count
        for sku_id, count in cart_dict.items():
            try:
                sku = GoodsSKU.objects.get(id=sku_id)
            except GoodsSKU.DoesNotExist:
                continue

            # 把count统一转换成int
            count = int(count)
            # 计算每种商品总价
            amount = count*sku.price

            # 动态给sku对象绑定count和amount,不会保存在数据库
            sku.count = count
            sku.amount = amount
            skus.append(sku)

            # 累计金额和数量
            total_count += count
            total_sku_amount += amount

        # 构造上下文
        context = {
            "skus":skus,
            "total_count":total_count,
            "total_sku_amount":total_sku_amount
        }

        # 渲染模板
        return render(request, "cart.html", context)




class AddCartView(View):
    """添加购物车"""

    def post(self,request):
        """接收ajax的post发来的购物车数据，存到redis"""

        # 判断用户是否登陆
        # if not request.user.is_authenticated():
        #     return JsonResponse({"code":1, "message":"用户未登录"})

        # 接收购物车数据，sku_id, count
        sku_id = request.POST.get("sku_id")
        count = request.POST.get("count")
        # 校验参数
        if not all([sku_id, count]):
            return JsonResponse({"code":2, "message":"缺少参数"})

        # 判断商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({"code":3, "message":"sku_id错误"})
        # 判断count是否是整数
        if re.match(r"^\d+$", count.decode()):
            count = int(count)
        else:
            return JsonResponse({"code":4, "message": "商品count错误"})

        # 判断库存 sku.stock
        if count > sku.stock:
            return JsonResponse({"code":5, "message":"库存不足"})

        # 判断用户是否登录
        if request.user.is_authenticated():
            # 获取user_id
            user_id = request.user.id

            # 加入购物车 保存到redis
            redis_conn = get_redis_connection("default")
            # 判断要添加的数据是否存在，如果存在，累加，不存在，赋值新值
            origin_count = redis_conn.hget("cart_%s" % user_id, sku_id)
            if origin_count is not None:
                count += int(origin_count)

            # 再次判断是否超出库存
            if count> sku.stock:
                return JsonResponse({"code": 5, "message": "库存不足"})

            redis_conn.hset("cart_%s" % user_id, sku_id, count)

            # 为了配合模板中js交互并展示购物车的数量，在这里需要查询一下购物车的总数
            cart_num = 0
            cart_dict = redis_conn.hgetall('cart_%s' % user_id)
            for val in cart_dict.values():
                cart_num += int(val)
            # json方式响应添加购物车结果
            return JsonResponse({"code":0, "message":"添加购物车成功", "cart_num":cart_num})
        else:
            # 用户未登录，使用cookie存储购物车数据,cart_json = '{"":"",}'
            cart_json = request.COOKIES.get("cart")

            if cart_json is not None:
                cart_dict = json.loads(cart_json)
            else:
                # 因为后面要使用cart_dict(遍历),所以定义一个空字典
                cart_dict = {}

            # 判断要添加的商品是否在cookie中，如果在，累加，不在，新赋值
            if sku_id in cart_dict:
                origin_count = cart_dict[sku_id]
                count += origin_count

            # 再次判断是否超出库存
            if count > sku.stock:
                return JsonResponse({"code": 5, "message": "库存不足"})
            # 存储新count
            cart_dict[sku_id] = count

            # 为了配合模板中js交互并展示购物车的数量，在这里需要查询一下购物车的总数
            cart_num = 0
            for val in cart_dict.values():
                cart_num += int(val)

            # 将最新的cart_dict转成json字符串
            new_cart_json = json.dumps(cart_dict)

            # 创建JsonResponse对象
            response = JsonResponse({"code":0, "message":"添加购物车成功", "cart_num":cart_num})

            response.set_cookie("cart", new_cart_json)

            return response
