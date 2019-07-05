from captcha.views import captcha_image
from django.conf.urls import include
from django.conf.urls import url
from django.urls import path

from users import views
from users.common.constants import CaptchaConstants

urlpatterns = [
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
    url(r"^captcha/", include("captcha.urls")),
    url(
        r"image/(?P<key>\w+)/$",
        captcha_image,
        name="captcha-image",
        kwargs={"scale": CaptchaConstants.CAPTCHA_SCALE_SIZE.value},
    ),
]
