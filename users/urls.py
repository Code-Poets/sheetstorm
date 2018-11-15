from django.conf.urls import url
from rest_framework import renderers
from rest_framework.urlpatterns import format_suffix_patterns
from users.views import UserViewSet
from users.views import UsersViewSet
from users.views import api_root

users_list = UsersViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

users_detail = UsersViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

user_account_detail = UserViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = format_suffix_patterns([
    url(r'^$', api_root),
    url(r'^users/$', users_list, name='users-list'),
    url(r'^users/(?P<pk>[0-9]+)/$', users_detail, name='users-detail'),
    url(r'^account/(?P<pk>[0-9]+)/$', user_account_detail, name='user-account-detail'),
])
