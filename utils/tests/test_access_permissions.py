from django.shortcuts import reverse
from django.test import TestCase

from employees.factories import ReportFactory
from users.factories import UserFactory
from users.models import CustomUser


class AccessPermissionsTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.report = ReportFactory()
        self.user = UserFactory()

    def test_sending_request_to_view_should_be_allowed_only_for_defined_user_types(self):
        urls_to_allowed_user_types = {
            # Employees.
            reverse("custom-report-list", kwargs={"year": 2019, "month": 5}): [
                CustomUser.UserType.EMPLOYEE.name,
                CustomUser.UserType.MANAGER.name,
                CustomUser.UserType.ADMIN.name,
            ],
            reverse("custom-report-detail", kwargs={"pk": self.report.pk}): [
                CustomUser.UserType.EMPLOYEE.name,
                CustomUser.UserType.MANAGER.name,
                CustomUser.UserType.ADMIN.name,
            ],
            reverse("custom-report-delete", kwargs={"pk": self.report.pk}): [
                CustomUser.UserType.EMPLOYEE.name,
                CustomUser.UserType.MANAGER.name,
                CustomUser.UserType.ADMIN.name,
            ],
            reverse("author-report-list", kwargs={"pk": self.user.pk, "year": 2019, "month": 5}): [
                CustomUser.UserType.ADMIN.name
            ],
            reverse("admin-report-detail", kwargs={"pk": self.report.pk}): [CustomUser.UserType.ADMIN.name],
            reverse("project-report-list", kwargs={"pk": self.report.project.pk, "year": 2019, "month": 5}): [
                CustomUser.UserType.MANAGER.name,
                CustomUser.UserType.ADMIN.name,
            ],
            reverse("project-report-detail", kwargs={"pk": self.report.pk}): [
                CustomUser.UserType.MANAGER.name,
                CustomUser.UserType.ADMIN.name,
            ],
            reverse(
                "export-data-xlsx",
                kwargs={
                    "pk": self.user.pk,
                    "year": self.report.creation_date.year,
                    "month": self.report.creation_date.month,
                },
            ): [CustomUser.UserType.ADMIN.name, CustomUser.UserType.MANAGER.name, CustomUser.UserType.EMPLOYEE.name],
            reverse(
                "export-project-data-xlsx",
                kwargs={
                    "pk": self.report.project.pk,
                    "year": self.report.creation_date.year,
                    "month": self.report.creation_date.month,
                },
            ): [CustomUser.UserType.MANAGER.name, CustomUser.UserType.ADMIN.name],
            # Managers.
            reverse("custom-projects-list"): [CustomUser.UserType.ADMIN.name, CustomUser.UserType.MANAGER.name],
            reverse("custom-project-create"): [CustomUser.UserType.ADMIN.name, CustomUser.UserType.MANAGER.name],
            reverse("custom-project-detail", kwargs={"pk": self.report.project.pk}): [
                CustomUser.UserType.ADMIN.name,
                CustomUser.UserType.MANAGER.name,
            ],
            reverse("custom-project-update", kwargs={"pk": self.report.project.pk}): [
                CustomUser.UserType.ADMIN.name,
                CustomUser.UserType.MANAGER.name,
            ],
            reverse("custom-project-delete", kwargs={"pk": self.report.project.pk}): [CustomUser.UserType.ADMIN.name],
            # Users.
            reverse("custom-users-list"): [CustomUser.UserType.ADMIN.name],
            reverse("custom-user-update-by-admin", kwargs={"pk": self.user.pk}): [CustomUser.UserType.ADMIN.name],
            reverse("custom-user-create"): [CustomUser.UserType.ADMIN.name],
        }

        # Iterate over all urls and all user types and check if response is 200 or 302.
        for url, allowed_user_types in urls_to_allowed_user_types.items():
            for user_type in CustomUser.UserType:

                with self.subTest(user_type=user_type, url=url):
                    user = UserFactory(user_type=user_type.name)
                    self.client.force_login(user)

                    self.report.author = user
                    self.report.full_clean()
                    self.report.save()
                    if user_type == CustomUser.UserType.MANAGER:
                        self.report.project.managers.set([user])

                    response = self.client.get(url)

                    if user_type.name in allowed_user_types:
                        self.assertEqual(
                            response.status_code,
                            200,
                            f'Response for url "{url}" for user type "{user_type.name}" is not 200.',
                        )
                    else:
                        self.assertIn(
                            response.status_code,
                            [302, 404],
                            f'Response for url "{url}" for user type "{user_type.name}" is not 302 or 404.',
                        )
                        self.assertRedirects(response, reverse("login") + f"?next={url}")
