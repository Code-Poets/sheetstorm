from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from users import views
from users.common import constants
from users.common.utils import generate_random_phone_number
from users.models import CustomUser


class UserUpdateByAdminTests(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it", password="newuserpasswd", first_name="John", last_name="Doe", country="PL"
        )
        self.user.full_clean()
        self.user.save()

    def test_user_update_by_admin_view_should_display_user_details_on_get(self):
        request = APIRequestFactory().get(path=reverse("custom-user-update-by-admin", args=(self.user.pk,)))
        request.user = self.user
        response = views.UserUpdateByAdmin.as_view()(request, pk=self.user.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.email)
        self.assertEqual(response.data["serializer"].instance, self.user)

    def test_user_update_by_admin_view_should_not_render_non_existing_user(self):
        not_existing_pk = 1000
        request = APIRequestFactory().get(path=reverse("custom-user-update-by-admin", args=(not_existing_pk,)))
        request.user = self.user
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
        request = APIRequestFactory().post(
            path=reverse("custom-user-update-by-admin", args=(self.user.pk,)),
            data={"email": self.user.email, "phone_number": invalid_phone_number},
        )
        response = views.UserUpdateByAdmin.as_view()(request, pk=self.user.pk)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(phone_number_before_request, self.user.phone_number)


class UserUpdateTests(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it", password="newuserpasswd", first_name="John", last_name="Doe", country="PL"
        )
        self.user.full_clean()
        self.user.save()

    def test_user_update_view_should_display_user_details_on_get(self):
        request = APIRequestFactory().get(path=reverse("custom-user-update", args=(self.user.pk,)))
        request.user = self.user
        response = views.UserUpdate.as_view()(request, pk=self.user.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.last_name)
        self.assertEqual(response.data["serializer"].instance, self.user)

    def test_user_update_view_should_not_render_non_existing_user(self):
        not_existing_pk = 1000
        request = APIRequestFactory().get(path=reverse("custom-user-update", args=(not_existing_pk,)))
        request.user = self.user
        response = views.UserUpdate.as_view()(request, pk=not_existing_pk)
        self.assertEqual(response.status_code, 404)

    def test_user_update_view_should_update_user_on_post(self):
        old_phone_number = generate_random_phone_number(constants.PHONE_NUMBER_MIN_LENGTH)
        self.user.set_password(self.user.password)
        self.user.save()
        self.client.login(email=self.user.email, password="newuserpasswd")
        request = self.client.get(path=reverse("custom-user-update", args=(self.user.pk,)))
        request.user = self.user
        response = self.client.post(
            path=reverse("custom-user-update", args=(self.user.pk,)), data={"phone_number": old_phone_number}
        )
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(old_phone_number, self.user.phone_number)

    def test_user_update_view_should_not_update_user_on_post_if_form_is_invalid(self):
        phone_number_before_request = self.user.phone_number
        old_phone_number = generate_random_phone_number(constants.PHONE_NUMBER_MIN_LENGTH - 1)
        request = APIRequestFactory().post(
            path=reverse("custom-user-update", args=(self.user.pk,)), data={"phone_number": old_phone_number}
        )
        request.user = self.user
        response = views.UserUpdate.as_view()(request, pk=self.user.pk)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(phone_number_before_request, self.user.phone_number)


class UserCreateTests(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it", password="newuserpasswd", first_name="John", last_name="Doe", country="PL"
        )
        self.user.full_clean()
        self.user.save()

    def test_user_create_view_should_display_create_user_form_on_get(self):
        request = APIRequestFactory().get(path=reverse("custom-user-create"))
        request.user = self.user
        response = views.UserCreate.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create new employee")

    def test_user_create_view_should_add_new_user_on_post(self):
        request = APIRequestFactory().post(
            path=reverse("custom-user-create"),
            data={
                "email": "anothertestuser@codepoets.it",
                "password1": "this_is_a_pass",
                "password2": "this_is_a_pass",
            },
        )
        request.user = self.user
        response = views.UserCreate.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/")
        self.assertEqual(CustomUser.objects.all().count(), 2)

    def test_user_create_view_should_not_add_new_user_on_post_if_form_is_invalid(self):
        request = APIRequestFactory().post(path=reverse("custom-user-create"), data={"email": "testuser@codepoets.it"})
        request.user = self.user
        response = views.UserCreate.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CustomUser.objects.all().count(), 1)


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
