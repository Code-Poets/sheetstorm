from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from users import views
from users.models import CustomUser


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
