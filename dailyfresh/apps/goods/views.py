from django.shortcuts import render
from django.views.generic import View
from goods.models import GoodsCategory,Goods,IndexGoodsBanner,IndexCategoryGoodsBanner,IndexPromotionBanner
# Create your views here.

class IndexView(View):
    """首页"""


    def get(self, request):
        """查询首页页面需要的数据，构造上下文，渲染首页页面"""

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

        # 查询购物车信息：目前没有实现，暂设为0
        cart_num = 0

        # 构造上下文
        context = {
            "categorys":categorys,
            "goods_banners":goods_banners,
            "promotion_banners":promotion_banners,
            "cart_num":cart_num
        }

        # 渲染模板
        return render(request, "index.html", context)