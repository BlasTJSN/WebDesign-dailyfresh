"""
Django settings for dailyfresh project.

Generated by 'django-admin startproject' using Django 1.8.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# 为了配合django用户认证系统模型类的使用，需要增加导包路径
import sys

sys.path.insert(1, os.path.join(BASE_DIR,"apps"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'jise8l@jz6_+2-_1#-_ng-k^gvw$wls5e8&vx=f0h^0pbkh5wh'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    # django用户认证系统的应用，默认使用
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # django的用户认证系统规定，在注册应用时，应用的名称需要跟AUTH_USER_MODEL = "users.User"里面的users保持一致
    "users",
    "goods",
    "orders",
    "cart",
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # 默认开启了用户认证的验证系统
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'dailyfresh.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,"templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dailyfresh.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "dailyfresh",
        "HOST": "192.168.90.39",  # MySQL数据库地址
        "PORT": "3306",
        "USER": "root",
        "PASSWORD": "mysql",
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

# 配置静态文件加载路径
STATIC_URL = '/static/'
STATICFIELS_DIRS = [
    os.path.join(BASE_DIR,"static")
]

# 配置django用户认证系统的模型类，将AbstractUser更换成User
# 说明：django的用户认证系统，只允许一级导包，只能有一个"."
AUTH_USER_MODEL = "users.User"


# 邮件服务器配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # 导入邮件模块
EMAIL_HOST = 'smtp.qq.com' # 发邮件主机
EMAIL_PORT = 587 # 发邮件端口
EMAIL_HOST_USER = '3393133521@qq.com' # 授权的邮箱
EMAIL_HOST_PASSWORD = 'ctsvjxbnixsadaaj' # 邮箱授权时获得的密码，非注册登录密码
EMAIL_FROM = '天天生鲜<3393133521@qq.com>' # 发件人抬头


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