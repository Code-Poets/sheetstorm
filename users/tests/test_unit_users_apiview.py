from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from users import views
from users.common import constants
from users.common.utils import generate_random_phone_number
from users.factories import AdminUserFactory
from users.models import CustomUser


class UserUpdateByAdminTests(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it", password="newuserpasswd", first_name="John", last_name="Doe", country="PL"
        )
        self.user.full_clean()
        self.user.save()
        self.user_admin = AdminUserFactory()
        self.client.force_login(self.user_admin)

    def test_user_update_by_admin_view_should_display_user_details_on_get(self):
        request = APIRequestFactory().get(path=reverse("custom-user-update-by-admin", args=(self.user.pk,)))
        request.user = self.user_admin
        response = views.UserUpdateByAdmin.as_view()(request, pk=self.user.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.email)
        self.assertEqual(response.data["serializer"].instance, self.user)

    def test_user_update_by_admin_view_should_not_render_non_existing_user(self):
        not_existing_pk = 1000
        request = APIRequestFactory().get(path=reverse("custom-user-update-by-admin", args=(not_existing_pk,)))
        request.user = self.user_admin
        response = views.UserUpdateByAdmin.as_view()(request, pk=not_existing_pk)
        self.assertEqual(response.status_code, 404)

    def test_user_update_by_admin_view_should_update_user_on_post(self):
        old_phone_number = generate_random_phone_number(constants.PHONE_NUMBER_MIN_LENGTH)
        response = self.client.post(
            path=reverse("custom-user-update-by-admin", args=(self.user.pk,)),
            data={"email": self.user.email, "phone_number": old_phone_number},
        )
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(old_phone_number, self.user.phone_number)

    def test_user_update_by_admin_view_should_not_update_user_on_post_if_form_is_invalid(self):
        phone_number_before_request = self.user.phone_number
        invalid_phone_number = generate_random_phone_number(constants.PHONE_NUMBER_MIN_LENGTH - 1)
        response = self.client.post(
            path=reverse("custom-user-update-by-admin", args=(self.user.pk,)),
            data={"email": self.user.email, "phone_number": invalid_phone_number},
        )
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(phone_number_before_request, self.user.phone_number)


class SignUpTests(TestCase):
    def setUp(self):
        self.user = CustomUser(email="testuser@codepoets.it", first_name="John", last_name="Doe", password="passwduser")
        self.user.full_clean()

    def test_signup_view_should_display_signup_form_on_get(self):
        request = APIRequestFactory().get(path=reverse("signup"))
        request.user = AnonymousUser()
        response = views.SignUp.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign up")

    def test_signup_view_should_add_new_user_on_post(self):
        response = self.client.post(
            path=reverse("signup"),
            data={
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "password1": self.user.password,
                "password2": self.user.password,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("success-signup"))
        self.assertEqual(CustomUser.objects.all().count(), 1)
