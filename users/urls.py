from django.conf.urls import include
from django.conf.urls import url
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from users import views

users_list = views.UsersViewSet.as_view({"get": "list", "post": "create"})

users_detail = views.UsersViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)

user_account_detail = views.UserViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)

urlpatterns = format_suffix_patterns(
    [
        path("accounts/password_reset/", views.CustomPasswordResetView.as_view(), name="password_reset"),
        path("accounts/password_reset/done/", views.CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
        path(
            "accounts/reset/<uidb64>/<token>/",
            views.CustomPasswordResetConfirmView.as_view(),
            name="password_reset_confirm",
        ),
        path("accounts/reset/done/", views.CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),
        path("accounts/password_change/", views.CustomPasswordChangeView.as_view(), name="password_change"),
        # TODO: Use only `django.contrib.auth.urls` that are needed, otherwise security issue.
        path("accounts/", include("django.contrib.auth.urls")),
        url(r"^api/users/$", users_list, name="users-list"),
        url(r"^api/users/(?P<pk>[0-9]+)/$", users_detail, name="users-detail"),
        url(r"^api/account/(?P<pk>[0-9]+)/$", user_account_detail, name="user-account-detail"),
        url(r"^$", views.index, name="home"),
        url(r"^signup/$", views.SignUp.as_view(), name="signup"),
        url(r"^user/$", views.UserUpdate.as_view(), name="custom-user-update"),
        url(r"^user/create/$", views.UserCreate.as_view(), name="custom-user-create"),
        url(r"^users/$", views.UserList.as_view(), name="custom-users-list"),
        url(r"^users/(?P<pk>[0-9]+)/$", views.UserUpdateByAdmin.as_view(), name="custom-user-update-by-admin"),
        url(r"^accounts/success/$", views.UserSignUpSuccess.as_view(), name="success-signup"),
        url(
            r"^activate/(?P<encoded_user_id>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
            views.ActivateAccountView.as_view(),
            name="activate",
        ),
    ]
)
