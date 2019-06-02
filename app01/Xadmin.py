from django.contrib import admin

# Register your models here.
print("app01 Xadmin")

from Xadmin.service.Xadmin import site,ModelXadmin

# print("app01 Xadmin")
from django.urls import reverse
from app01.models import *
from django.utils.safestring import mark_safe
from django.forms import ModelForm

class BookFormDemo(ModelForm):
    class Meta:
        model = Book
        fields = "__all__"
        labels = {
            "title": "书名",
            "price": "价格"
        }

class Bookconfig(ModelXadmin):

    list_display = ['title', 'price','publishDate','publish','authors']
    list_display_links = ['title']
    modelform_class = BookFormDemo
    search_fields = ["title", "price"]

    list_filter = ["title","publish", "authors"]

    def patch_init(self, request, queryset):
        print(queryset)

        queryset.update(price=123)
    patch_init.short_description = "批量初始化"
    actions = [patch_init]

class Authorscongif(ModelXadmin):
    # list_display = ['name']
    pass
site.register(Book, Bookconfig)
site.register(Publish)
site.register(Author,Authorscongif)
site.register(AuthorDetail)
