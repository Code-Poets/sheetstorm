from rest_framework.urlpatterns import format_suffix_patterns

from django.conf.urls import url
from django.conf.urls import include
from django.urls import path

from users import views


users_list = views.UsersViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

users_detail = views.UsersViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

user_account_detail = views.UserViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = format_suffix_patterns([
    url(r'^api/$', views.api_root),
    url(r'^api/users/$', users_list, name='users-list'),
    url(r'^api/users/(?P<pk>[0-9]+)/$', users_detail, name='users-detail'),
    url(r'^api/account/(?P<pk>[0-9]+)/$', user_account_detail, name='user-account-detail'),
    url(r'^$', views.index, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    url(r'^signup/$', views.SignUp.as_view(), name='signup'),
    url(r'^user/(?P<pk>[0-9]+)/$', views.UserUpdate.as_view(), name='custom-user-update'),
    url(r'^user/create/$', views.UserCreate.as_view(), name='custom-user-create'),
    url(r'^users/$', views.UserList.as_view(), name='custom-users-list'),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view(), name='custom-users-detail'),
])
