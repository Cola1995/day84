from django.contrib import admin

# Register your models here.
print("app02 Xadmin")
from Xadmin.service.Xadmin import site,ModelXadmin
from app02.models import *


class Foodconfig(ModelXadmin):
    list_display = ['title']


site.register(Food, Foodconfig)
site.register(Order)