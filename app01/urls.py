from django.conf.urls import url, include
from django.contrib import admin
from  app01 import views
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'index/', views.index),

]
