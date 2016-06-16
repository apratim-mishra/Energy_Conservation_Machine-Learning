"""smart_home_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.views.generic.base import TemplateView
from django.conf.urls import include, url
from django.contrib import admin

from smart_home_app import views
import os
from django.conf.urls.static import static
from django.conf import settings

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATE_DIRS = os.path.join(BASE_DIR, 'templates')

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^smart_home_app/$', views.smart_home_api),
]


# see https://docs.djangoproject.com/en/1.8/howto/static-files/
# Put files under static directory
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)


