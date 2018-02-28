from django.shortcuts import render
from django.views.generic import View
from goods.models import GoodsCategory,Goods,IndexGoodsBanner,IndexCategoryGoodsBanner,IndexPromotionBanner
from django.core.cache import cache
from django_redis import get_redis_connection
from django.core.urlresolvers import reverse
# Create your views here.

class IndexView(View):
    """首页"""


    def get(self, request):
        """查询首页页面需要的数据，构造上下文，渲染首页页面"""

        # 查询是否有缓存：存储数据类型和读取数据类型相同
        context = cache.get("index_page_data")
        if context is None:
            # 没有缓存，查询数据

            # 查询用户个人信息，在request.user中

            # 查询商品分类信息
            categorys = GoodsCategory.objects.all()

            # 查询图片轮播信息：按index进行排序，默认从小到大排序
            goods_banners = IndexGoodsBanner.objects.all().order_by("index")

            # 查询商品活动信息
            promotion_banners = IndexPromotionBanner.objects.all().order_by("index")

            # 查询商品分类列表展示信息
            for category in categorys:
                # 查询此类别中用图片展示的信息
                image_banners = IndexCategoryGoodsBanner.objects.filter(category=category, display_type=1)
                # 更新categorys中的category中的信息
                category.image_banners = image_banners

                # 查询此类别中用标签展示的信息
                title_banners = IndexCategoryGoodsBanner.objects.filter(category=category, display_type=0)
                category.title_banners = title_banners
                # 构造上下文
                context = {
                    "categorys": categorys,
                    "goods_banners": goods_banners,
                    "promotion_banners": promotion_banners,
                }

                # 缓存context:缓存的key 要缓存的内容 超时时间
                cache.set("index_page_data", context, 3600)
        # 查询购物车信息：目前没有实现，暂设为0
        cart_num = 0

        # 如果是登陆用户，需要查询保存在redis中的购物车数据
        if request.user.is_authenticated():

            # 创建连接到redis的对象
            redis_conn = get_redis_connection("default")

            # 调用hgetall()，查询hash对象中所有的数据,返回字典（字典的key和value是bytes类型）
            user_id = request.user.id
            cart_dict = redis_conn.hgetall("cart_%s" % user_id)

            # 遍历字典，读取商品数量，求和
            for val in cart_dict.values():
                cart_num += int(val)

        # 更新context
        context.update(cart_num=cart_num)

        # 渲染模板
        return render(request, "index.html", context)