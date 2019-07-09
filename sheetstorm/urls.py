"""sheetstorm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import include

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^", include("users.urls")),
    url(r"^managers/", include("managers.urls")),
    url(r"^", include("employees.urls")),
    # url(r"^select2/", include("django_select2.urls")),
]
