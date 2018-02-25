# dailyfresh
天天生鲜电商项目
1.创建dailyfresh项目


2.创建应用cart,goods,orders,users


3.定义模型类

3.1.分别在users、goods、orders应用中定义好对应的模型类

3.2.cart应用中暂时不定义模型类，其中的数据是使用redis数据库维护的

3.3 安装itsdangerous模块


4.User模型

4.1.users应用中的模型类User是使用Django自带的用户认证系统维护的，Django中默认开启用户认证模块中间件

4.2.迁移前，需要在settings.py文件中设置：AUTH_USER_MODEL = '应用.用户模型类',即AUTH_USER_MODEL = 'users.User'


5.增加导包路径

5.1.原因：在settings.py中设置AUTH_USER_MODEL时，编码规则为'应用.用户模型类'

5.2.但是，应用在apps/文件目录下，为了保证正确的编码，我们需要增加导包路径

5.3.同时，为了配合AUTH_USER_MODEL的配置，应用的安装直接使用users，不要使用apps.users

5.4.
 import sys
  sys.path.insert(1, os.path.join(BASE_DIR, 'apps'))


6.URL配置

6.1.安装pymysql

6.2.配置模板加载路径

6.3.配置静态文件加载路径


7.模型迁移


8.展示注册页面

9.展示注册页面

9.1.在users中定义注册页面视图，使用类视图

9.2.准备模板

9.3.匹配url


10.实现注册逻辑

10.1.获取注册请求参数

10.2.教研注册请求参数

10.2.1前后端的校验需要分离：前端检验完，数据到服务器后继续校验，避免黑客绕过客户端发请求

10.2.2提示：出现异常的处理方式，根据公司具体需求来实现

10.3保存用户注册信息

10.3.1.隐私信息需要加密，可以直接使用django提供的用户认证系统完成，不需要save()

10.3.2.调用create_user(user_name, email, password)实现用户保存和加密隐私信息，参数顺序不能错

10.3.3.IntegrityError异常用于判断用户是否重名、已注册，这样可以减少访问数据库频率

10.3.4.保存完用户注册信息后，需要重置用户激活状态，因为Django用户认证系统默认激活状态为True


11.实现邮件激活

11.1定义邮件激活类视图

11.2使用itsdangerous模块生成激活token

11.2.1生成用户激活token的方法封装在User模型类中.

Serializer()生成序列化器，传入混淆字符串和过期时间.

dumps()生成user_id加密后的token，传入封装user_id的字典.
返回token字符串.

loads()解出token字符串，得到用户id明文.

11.3Celery异步发送激活邮件

11.3.0配置邮件服务器和发件人sender

11.3.1创建Celery异步任务文件celery_tasks/tasks.py

11.3.2.创建应用对象/客户端/client

Celery()：

参数1是异步任务路径.

参数2是指定的broker.

redis://密码@redis的ip:端口/数据库.

redis://192.168.243.191:6379/4.

返回客户端应用对象app.

send_active_email()：内部封装激活邮件内容，并用装饰器@app.task注册.

调用python的send_mail()将激活邮件发送出去.

11.3.3将redis数据库作为中间人borker

11.4实现激活逻辑


12.实现登陆逻辑


13.登陆记住用户

13.1安装django-redis模块，配置django-redis

13.2设置session时间来实现记住用户逻辑


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



