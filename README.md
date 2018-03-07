# dailyfresh
天天生鲜电商项目

#### 1.创建dailyfresh项目

#### 2.创建应用cart,goods,orders,users
- 2.1 安装应用

#### 3.定义模型类

- 3.1.分别在users、goods、orders应用中定义好对应的模型类
    - 3.1.1 定义基类BaseModel模型类，作为所有模型类的父类使用，表示所有模型类共有的属性，create_time和update_time字段
    - 3.1.2 定义User模型类
    需要继承AbstractUser父类，AbstractUser让模型类User使用Django自带的用户认证系统
    Django中默认开启用户认证模块中间件
    定义生成激活令牌方法用于邮件激活操作
    迁移前，需要在settings.py文件中设置：AUTH_USER_MODEL = '应用.用户模型类',即AUTH_USER_MODEL = 'users.User'
    - 3.1.3 定义Address模型类，字段包括id,user,receiver_name,receiver_mobile,detail_addr,zip_code
    User模型类作为外键，多对一的关系
    - 3.1.4 定义GoodsCategory模型类,表示商品类别，字段包括id,name,logo,image
    - 3.1.5 定义GoodsCategory模型类，表示商品SPU，字段包括id,name,desc(详细介绍)
    - 3.1.6 定义GoodsSKU模型类，表示商品SKU，字段包括id,category,goods,name,title,unit,price,stock,sales,default_image,status
    GoodsCategory模型类作为外键，多对一关系
    Goods模型类作为外键，多对一关系
    - 3.1.7 定义GoodsImage模型类，表示商品图片，字段包括id,sku,image
    GoodsSKU模型类作为外键，多对一关系
    - 3.1.8 定义IndexGoodsBanner模型类，表示主页轮播商品展示，字段包括id,sku,image,index(轮播顺序)
    GoodsSKU模型类作为外键，多对一关系
    - 3.1.9 定义IndexCategoryGoodsBanner模型类，表示主页分类商品展示，字段包括id,category,sku,display_type,index
    GoodsCategory模型类作为外键，多对一关系
    GoodsSKU模型类作为外键，多对一关系
    - 3.1.10 定义IndexPromotionBanner模型类，表示主页促销活动，字段包括id,name,url,image,index
    - 3.1.11 定义OrderInfo模型类，表示订单信息，字段包括order_id,user,address,total_count,total_amount,trans_cost,pay_method,status,trade_id
    User模型类作为外键，多对一关系
    Address模型类作为外键，多对一关系
    - 3.1.12 定义OrderGoods模型类，表示订单商品，字段包括id,order,sku,count,price,comment
    OrderInfo模型类作为外键，多对一关系
    GoodsSKU模型类作为外键，多对一关系

- 3.2 cart应用中暂时不定义模型类，其中的数据是使用redis数据库维护的
- 3.3 基类BaseModel作为工具类，放在/utils/models.py中
- 3.4 安装itsdangerous模块，用于生成token,邮箱激活使用
- 3.5 安装django-tinymce模块,用于富文本编辑

#### 4.增加导包路径

- 4.1.原因：在settings.py中设置AUTH_USER_MODEL时，编码规则为'应用.用户模型类'
- 4.2.但是，应用在apps/文件目录下，为了保证正确的编码，我们需要增加导包路径
- 4.3.同时，为了配合AUTH_USER_MODEL的配置，应用的安装直接使用users，不要使用apps.users
``` python
import sys
sys.path.insert(1, os.path.join(BASE_DIR, 'apps'))
```

#### 5.URL配置
- 5.1.安装pymysql, DATABASES={}
- 5.2.配置模板加载路径 , TEMPLATES={}
- 5.3.配置静态文件加载路径

#### 6.模型迁移

#### 7.实现注册页面
- 7.1 在users中定义注册页面类视图 RegisterView(View)
- 7.2 准备模板register.html
- 7.3 匹配url
- 7.4 注册逻辑的实现
    - 7.4.1 处理post请求
        - 接收表单提交的参数
        - 进行参数校验
            - 判断是否缺少参数
            - 判断两次密码是否一致
            - 判断邮箱格式
            - 判断是否勾选了用户协议
        - 保存注册请求参数
            - 调用create_user(user_name, email, password)实现用户保存和加密隐私信息，参数顺序不能错
            - 抛出异常判断用户是否已存在
        - 重置激活状态为False
        - 生成激活令牌token，调用User模型类方法
        - 异步发送激活邮件，delay触发异步任务
        - 响应结果

#### 8.实现用户激活
- 8.1 配置邮件服务器和发件人sender:3393133521@qq.com
- 8.2 settings.py中配置邮件服务器参数
``` python
# 邮件服务器配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # 导入邮件模块
EMAIL_HOST = 'smtp.qq.com' # 发邮件主机
EMAIL_PORT = 587 # 发邮件端口
EMAIL_HOST_USER = '3393133521@qq.com' # 授权的邮箱
EMAIL_HOST_PASSWORD = 'ctsvjxbnixsadaaj' # 邮箱授权时获得的密码，非注册登录密码
EMAIL_FROM = '天天生鲜<3393133521@qq.com>' # 发件人抬头

```
- 8.3 使用Celery,用于处理异步任务(client,broker,worker)
    - 8.3.1 安装Celery
    - 8.3.2 创建Celery异步任务文件/celery_tasks/tasks.py
    - 8.3.3 发送封装好内容的激活邮件的逻辑的实现
        - 创建Celery客户端(client)，创建应用对象app,指定broker为redis
        - app.task装饰器装饰发送激活邮件函数
        - 定义发送激活邮件函数send_active_email(to_email, user_name, token)
            - 封装邮件内容
            - 发送邮件send_mail()
        - 创建worker
            - 拷贝项目代码到其他服务器中
            - 在/celery_tasks/tasks.py文件顶部添加加载Django环境配置的代码
            - 终端执行命令创建worker
        - **开启redis-server**
- 8.4 激活逻辑实现
    - 8.4.1 定义用户激活类视图，配置url
    - 8.4.2 处理get请求，接收和处理激活
        - 创建序列化器，参数和调用dumps方法的相同
        - 获取token
            - 判断激活链接是否过期
        - 读取user_id
        - 查询要激活的用户
            - 判断用户是否存在
        - 重置激活状态为True
        - 响应结果

#### 9.实现用户登录
- 9.1 使用redis数据库缓存session信息
    - 9.1.1 安装django-redis
    - 9.1.2 settings.py文件配置django-redis,login()会自动调用SESSION_ENGINE指定的缓存方式（这里使用redis）
    ``` python
    # 缓存
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://192.168.90.39:6379/5",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }

    # Session
    # http://django-redis-chs.readthedocs.io/zh_CN/latest/#session-backend

    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"
    ```
- 9.2实现登录逻辑
    - 9.2.1定义用户登陆类视图，配置url
    - 9.2.2 处理post请求，处理登录逻辑
        - 接收用户登录表单数据user_name,pwd
        - 对用户进行验证，使用Django用户认证系统
            - 判断用户是否存在
            - 判断用户是否激活
        - 登陆用户login(),将用户状态保持信息存储到redis
        - 获取勾选记住用户名数据
        - 判断是否勾选记住用户名
            - 未勾选，设置状态保持时间为0
            - 勾选，设置状态保持时间为默认值14天
        - -----此处为购物车逻辑----- 在页面跳转前，将cookie中的购物车数据添加到redis中
        - 获取cookies中购物车的数据cart_json
        - 判断cart_json是否存在
            - 存在，将数据转换成JSON格式（读取明文，字典格式）
            - 不存在，定义空字典
        - 查询redis中购物车数据，得到购物车数据（字典格式）
        - 遍历cookies中的购物车数据
            - 判断cookies中的商品在redis中是否存在
                - 存在，读取redis中购物车商品数量
                - 合并购物车数量
                - 查询商品信息，判断购物车数量是否超过库存
            - 将合并后的数据更新到redis中取出的购物车字典中
        - 将合并后的数据更新到redis中的购物车数据中
        - -----此处为购物车逻辑-----
        - 判断地址是否有next参数
            - 没有，响应到主页
#### 10.实现用户退出
- 10.1实现退出逻辑
    - 10.1.1 定义退出登录类视图，配置url
    - 10.1.2 处理get请求
        - 调用logout()


14.退出登陆

15.提供用户地址信息

15.1定义用户地址类视图

15.2限制页面访问

15.2.1@login_required装饰器，实现只允许登陆用户访问的功能

15.2.1.1注意使用@login_required装饰器时需要配置settings.py,添加LOGIN_URL = '/users/login'，指定验证失败后跳转到的路径。

15.2.2如果是登陆用户，则进入被装饰的视图，如果不是登陆用户，则跳转到settings.py中指定的路径，并且在路径中添加?next="进入被装饰视图的匹配路径"

15.2.3装饰类视图时，采取多继承的方法

15.2.4定义一个拓展类用来重写as_view方法，并将装饰器装饰在这个拓展类的as_view方法返回的视图上。将这个拓展类封装为一个模块，放在utils中

15.2.5用户地址类视图继承拓展类和View类，根据MRO排序，拓展类中super().as_view()方法会在View类中找到并调用，以此完成类视图的装饰及调用

16.给登陆视图添加next跳转功能

16.1.?next=""通过GET请求获取相关数据

17收货地址页面视图编写

17.1最新收货地址数据显示，通过模型类获取用户地址数据，通过GET请求渲染模板

17.2提交编辑的新地址，通过POST请求获取提交的数据，向数据库添加新数据

18个人信息页面视图编写

18.1也需要验证登录用户

18.2获取用户信息，方法同收货地址视图

18.3浏览记录获取
18.3.1通过把不同用户的id作为键，商品SKUid作为值存入redis中

18.3.2在个人信息视图中建立与redis的连接，获取对应用户对应的skuid

18.3.3按浏览排序取出GoodsSKU中对应id中相关数据,因为从redis中取数据的顺序和存数据相反，所以要新建一个列表把取出的数据添加进去，保证与存入的顺序即浏览顺序一致

18.3.4渲染模板

19抽离父模板

19.1 继承父模板重写收货地址，个人信息模板

20.安装FastDFS服务器

20.1使用FastDFS服务器存储图片数据。使用nginx读取FastDFS服务器的图片数据

21完成Django对接FastDFS流程

21.1整体流程
21.1.1浏览器后台站点发布图片，向Django发出上传图片请求
21.1.2Django得到上传图片请求信息，调用上传图片方法client.upload_by_buffer(file_data),调用fdfs客户端
21.1.3fdfs客户端得到上传请求信息，传递请求信息到FastDFS服务器,通过client.conf传递到指定的服务器
21.1.4tracker得到请求信息，查询可用的storage，再通过client.conf返回可用的storage的ip和端口到fdfs客户端
21.1.5fdfs客户端把图片传给指定的storage
21.1.6storage接收图片，将上传的图片写入服务器，同时生成存储位置的file_id，把status+file_id+文件名+Storage_IP返回给fdfs客户端
21.1.7fdfs客户端判断是否上传成功，返回file_id到Django
21.1.8Django把file_id存储到数据库
21.1.9用户访问页面，向Django发出html请求，通过模板中的标签查询数据库中图片的file_id
21.1.10使用nginx从服务器磁盘中读取图片数据，渲染html页面

21.2安装fdfs_client,用于fdfs与Django的交互

21.3实现自定义文件存储系统storage

21.3.1建立自定义文件存储系统目录结构utils/fastdfs/client.conf,utils/fastdfs/storage.py

21.3.2配置settings.py中Django自定义的存储系统

21.3.3在storage.py中实现自定义存储系统类的代码逻辑

21.4测试自定义文件存储系统后台站点上传图片
21.4.1本地化
21.4.2注册模型类到后台站点
21.4.3创建超级管理员并登陆进入到后台站点
21.4.4发布内容

22.添加富文本编辑器功能

23.后台站点上传图片数据，数据库加入商品数据

24.主页商品信息展示
24.1定义主页类视图
24.2渲染index.html模板

25.页面静态化
25.1celery生成静态html,在task.py中渲染模板static_index.html
25.2配置nginx访问静态html,在/usr/local/nginx/conf中配置
25.3模型管理类地啊用celery异步方法,在admin.py中封装BaseAdmin类

26.动态主页html缓存
26.1判断是否存在缓存，不存在就执行数据查询缓存
26.2购物车是实时变化的不能被缓存
26.3缓存需设置有效时间，才能让数据更新

27.实现主页购物车，数量统计
27.1购物车数据保存在redis中，使用hash格式cart_userid sku_id count

28.实现详情页面
28.1查询商品SKU信息，查询所有商品分类信息，查询商品订单评论信息，查询新商品推荐，查询其他规格商品，如果已登陆，查询购物车信息
28.2实现存储浏览记录的逻辑

29.实现商品列表页面
29.1查询商品分类信息，查询新品推荐信息，查询商品列表信息，查询商品分页信息，查询购物车信息

30.全文检索
30.1安装haystack应用
30.2在settings.py文件中配置搜索引擎
30.3在要索引的表的应用下创建search_indexes.py文件，定义商品索引类GoodsSKUIndex()，继承自indexes.SearchIndex和indexes.Indexable
30.4在templates下新建目录search/indexes/goods,新建goodssku_text.txt，并编辑要建立索引的字段
30.5 生成索引文件 python manage.py rebuild_index
30.6搜索表单处理
30.7配置搜索地址正则
30.8编写search.html模板
30.9 使用中文分词工具jieba

31.购物车
31.1定义添加购物车视图
31.2实现用户登陆时添加购物车视图和模板渲染，购物车数据存储在redis中
31.3实现未登录时添加购物车视图和模板渲染，购物车数据存储在cookie中
31.4登陆后将cookie中的数据合并到redis中

31.5封装goods应用下的购物车数量逻辑，定义BaseCartView类视图

31.6实现购物车页面
31.6.1配置url
31.6.2定义获取购物车数据类视图，渲染模板

31.7用户登陆时购物车合并cookie和redis数据

31.8购物车更新设计，采用幂等接口，每次传输的都是商品的最终数量
31.8.1 购物车前段代码编写
31.8.2更新页面合计信息，更新页面顶端全部商品数量，更新后端购物车信息，增加商品数量，减少商品数量，手动输入商品数量，商品对应的checkbox发生改变时，全选checkbox发生改变，全选和全不选

31.9删除购物车记录
31.9.1用户登录，删除redis中的数据,未登录，删除cookie中的购物车记录


32.订单确认页面
32.1定义订单确认类视图，配置url
32.1.1获取请求页面的sku_id和count,如果count为None,则证明用户是从购物车页面请求的，从redis中获取数据,如果count不为None，则证明用户是从详情页面请求的,从request中获取数据
32.2渲染订单确认页面模板

33.提交订单逻辑
33.1提交订单页面使用ajax处理数据，所以不进行页面跳转，登陆认证通过json返回给ajax登录情况，需要新定义一个装饰器实现此逻辑
33.2提交订单事务支持
33.2.1 保证在没有错误时，执行保存数据的操作，其他情况回滚
33.2.2使用atomic装饰器，提供数据库事务功能

33.3提交订单乐观锁支持
33.3.1使用乐观锁将要操作的更新库存记录锁起来，判断更新时的库存和之前已经查出的库存是否一致
33.3.2每个订单设计三次提交订单的机会

34.我的订单页面
34.1定义用户订单页面类视图，配置url
34.2渲染模板

35提交订单到支付宝
35.1登陆支付宝开放平台
35.2电脑网站支付快速接入
35.2.1创建应用，添加电脑网站支付功能
35.2.2配置密钥，沙箱中添加公钥，应用中配置私玥和支付宝提供的公玥
35.2.3搭建和配置开发环境
35.3定义支付类视图，实现逻辑，配置url,settings.py配置对接支付宝
35.4定义订单状态类视图，实现逻辑，配置url
35.5定义订单评论类视图，实现逻辑，配置url

36配置uWSGI

37nginx操作
37.1配置两个uwshi.ini文件
37.2配置nginx的server
37.3在settings.py中配置，指定项目静态文件
收集路径

