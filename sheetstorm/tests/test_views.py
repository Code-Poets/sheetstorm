from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from sheetstorm.views import Index
from users.factories import UserFactory


class IndexPageTests(TestCase):
    def setUp(self):
        self.url = reverse("home")
        self.user = UserFactory()

    def test_not_logged_user_got_redirected_to_login_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_logged_user_go_to_home_page(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, Index.template_name)
