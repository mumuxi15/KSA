from .base import *
from ksa_api.env import env

ALLOWED_HOSTS = ['localhost','127.0.0.1']
DEBUG = env.bool('DJANGO_DEBUG', default = True)

DATABASES['work'] =  {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': env('PYODBC_CONNECTION_STRING')
    }

