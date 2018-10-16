from django.test import TestCase
from users.models import CustomUser
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.test import APIClient


class TestCustomUserLogin(TestCase):
    def setUp(self):
        user = CustomUser.objects._create_user(
            "testuser@example.com",
            "testuserpasswd",
            False,
            False,
        )

    def test_that_user_should_login_correctly(self):
        self.assertTrue(self.client.login(
            email="testuser@example.com",
            password="testuserpasswd",
            )
        )

    def test_that_user_should_not_login_correctly_with_wrong_email(self):
        self.assertFalse(self.client.login(
            email="wrongtestuser@example.com",
            password="testuserpasswd",
            )
        )

    def test_that_user_should_not_login_correctly_with_wrong_password(self):
        self.assertFalse(self.client.login(
            email="testuser@example.com",
            password="wrongtestuserpasswd",
            )
        )

    def test_that_user_should_not_login_correctly_with_no_email(self):
        self.assertFalse(self.client.login(
            email=None,
            password="wrongtestuserpasswd",
            )
        )

    def test_that_user_should_not_login_correctly_with_no_password(self):
        self.assertFalse(self.client.login(
            email="testuser@example.com",
            password=None,
            )
        )


class TestCustomUserModel(TestCase):
    def test_that_user_should_be_created_correctly(self):
        try:
            new_user = CustomUser.objects._create_user(
                "testuser@example.com",
                "testuserpasswd",
                False,
                False,
            )
        except:
            new_user = None
        self.assertFalse(new_user is None)

    def test_that_user_should_be_in_database_after_creation(self):
        new_user = CustomUser.objects._create_user(
            "testuser@example.com",
            "testuserpasswd",
            False,
            False,
        )
        try:
            search_user = CustomUser.objects.get(email="testuser@example.com")
        except CustomUser.DoesNotExist:
            search_user = None
        self.assertTrue(search_user is not None)

    def test_that_user_should_not_be_in_database_after_creation(self):
        new_user = CustomUser.objects._create_user(
            "testuserexample.com",
            "testuserpasswd",
            False,
            False,
        )
        try:
            search_user = CustomUser.objects.get(email="testuser@example.com")
        except CustomUser.DoesNotExist:
            search_user = None
        self.assertTrue(search_user is None)
