import os
os.environ["DJANGO_SETTINGS_MODULE"] = "dailyfresh.settings"
# 放到celery服务器上时将注释打开
#import django
#django.setup()



from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
from goods.models import GoodsCategory, Goods, GoodsSKU, IndexGoodsBanner, IndexCategoryGoodsBanner, IndexPromotionBanner
from django.template import loader


# 创建celery客户端,参数1是异步任务位置，参数2是任务存放的队列
app = Celery("celery_tasks.tasks", broker="redis://192.168.90.39:6379/4")


# 定义异步任务
@app.task
def send_active_email(to_email, user_name, token):
    """发送激活邮件"""
    subject = "天天生鲜用户激活" # 标题
    body = "" # 文本邮件体
    sender = settings.EMAIL_FROM # 发件人
    receiver = [to_email] # 接收人
    html_body = '<h1>尊敬的用户 %s, 感谢您注册天天生鲜！</h1>' \
                '<br/><p>请点击此链接激活您的帐号<a href="http://127.0.0.1:8000/users/active/%s">' \
                'http://127.0.0.1:8000/users/active/%s</a></p>' % (user_name, token, token)
    send_mail(subject, body, sender, receiver, html_message=html_body)


@app.task
def generate_static_index_html():
    """异步生成主页的静态页面"""

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

    # 查询购物车信息：静态主页中不要写购物车真实数据，默认为0
    cart_num = 0

    # 构造上下文
    context = {
        "categorys": categorys,
        "goods_banners": goods_banners,
        "promotion_banners": promotion_banners,
        "cart_num": cart_num
    }

    # 得到模板
    template = loader.get_template("static_index.html")

    # 使用上下文渲染模板，得到模板数据：不需要相应给用户，不需要user信息
    html_data = template.render(context)

    # 放在静态（celery）服务器存储
    # 这个异步任务是被celery服务器阅读的，所以生成的html_data需要存储在celery服务器的某个路径下，管理静态文件的路径下
    file_path = os.path.join(settings.STATICFILES_DIRS[0], "index.html")
    with open(file_path, "w") as file:
        file.write(html_data)

