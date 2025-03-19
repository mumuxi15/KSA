from .base import *
from ksa_api.env import env
DEBUG = env.bool('DJANGO_DEBUG', default = False)

