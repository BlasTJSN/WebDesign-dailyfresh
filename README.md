# dailyfresh
天天生鲜电商项目
1.创建dailyfresh项目
2.创建应用cart,goods,orders,users
3.定义模型类
3.1.分别在users、goods、orders应用中定义好对应的模型类
3.2.cart应用中暂时不定义模型类，其中的数据是使用redis数据库维护的
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
6.2.修改视图路径
7.模型迁移
