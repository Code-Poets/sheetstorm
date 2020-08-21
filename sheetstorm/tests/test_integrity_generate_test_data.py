from django.core import management
from django.core.management.base import CommandError
from django.test import TestCase
from parameterized import parameterized

from managers.models import Project
from sheetstorm.management.commands.generate_test_data import ProjectType
from users.factories import UserFactory
from users.models import CustomUser


class CreateUsersTests(TestCase):
    def test_that_command_should_create_superuser_when_superuser_is_requested(self):
        management.call_command("generate_test_data", SUPERUSER=True)

        self.assertTrue(CustomUser.objects.filter(is_superuser=True).exists())

    def test_that_command_should_not_create_superuser_when_superuser_is_not_requested(self):
        management.call_command("generate_test_data")

        self.assertFalse(CustomUser.objects.filter(is_superuser=True).exists())

    def test_that_command_should_not_create_superuser_when_superuser_is_requested_but_already_exists(self):
        UserFactory(is_superuser=True)

        management.call_command("generate_test_data", SUPERUSER=True)

        self.assertEqual(CustomUser.objects.filter(is_superuser=True).count(), 1)

    @parameterized.expand(
        [
            (CustomUser.UserType.ADMIN.name, 3),
            (CustomUser.UserType.EMPLOYEE.name, 5),
            (CustomUser.UserType.MANAGER.name, 4),
        ]
    )
    def test_that_result_of_command_should_be_specified_number_of_users_in_database(
        self, user_type, number_of_users_to_create
    ):
        management.call_command("generate_test_data", **{user_type: number_of_users_to_create})

        self.assertEqual(CustomUser.objects.filter(user_type=user_type).count(), number_of_users_to_create)

    def test_that_command_should_not_create_any_user_when_any_argument_is_not_specified(self):
        management.call_command("generate_test_data")

        self.assertEqual(CustomUser.objects.all().count(), 0)

    @parameterized.expand(
        [
            (CustomUser.UserType.ADMIN.name, 2),
            (CustomUser.UserType.EMPLOYEE.name, 2),
            (CustomUser.UserType.MANAGER.name, 2),
        ]
    )
    def test_that_command_should_not_require_all_arguments_to_create_specified_users(
        self, user_type, number_of_users_to_create
    ):
        management.call_command("generate_test_data", **{user_type: number_of_users_to_create})

        self.assertEqual(CustomUser.objects.filter(user_type=user_type).count(), number_of_users_to_create)

    @parameterized.expand(
        [
            (CustomUser.UserType.ADMIN.name, 0, 0),
            (CustomUser.UserType.ADMIN.name, -100, 0),
            (CustomUser.UserType.ADMIN.name, 2, 2),
            (CustomUser.UserType.EMPLOYEE.name, 0, 0),
            (CustomUser.UserType.EMPLOYEE.name, -100, 0),
            (CustomUser.UserType.EMPLOYEE.name, 2, 2),
            (CustomUser.UserType.MANAGER.name, 0, 0),
            (CustomUser.UserType.MANAGER.name, -100, 0),
            (CustomUser.UserType.MANAGER.name, 2, 2),
        ]
    )
    def test_that_command_should_not_create_users_when_specified_number_is_not_greater_than_0(
        self, user_type, number_of_users_to_create, expected_number_of_users_in_database
    ):
        management.call_command("generate_test_data", **{user_type: number_of_users_to_create})

        self.assertEqual(CustomUser.objects.filter(user_type=user_type).count(), expected_number_of_users_in_database)

    @parameterized.expand(
        [
            (CustomUser.UserType.ADMIN.name, 1),
            (CustomUser.UserType.EMPLOYEE.name, 1),
            (CustomUser.UserType.MANAGER.name, 1),
        ]
    )
    def test_that_despite_filled_database_command_should_create_specified_number_of_users(
        self, user_type, number_of_users
    ):
        management.call_command("generate_test_data", **{user_type: number_of_users})

        management.call_command("generate_test_data", **{user_type: number_of_users + 1})

        self.assertEqual(CustomUser.objects.filter(user_type=user_type).count(), number_of_users + 1)


class CreateProjectsTests(TestCase):
    def test_that_result_of_command_should_be_specified_number_of_projects_in_database(self):
        number_of_projects_to_create = {
            ProjectType.SUSPENDED.name: 4,
            ProjectType.ACTIVE.name: 3,
            ProjectType.COMPLETED.name: 2,
        }

        management.call_command("generate_test_data", **number_of_projects_to_create)

        self.assertEqual(
            Project.objects.filter_suspended().count(), number_of_projects_to_create[ProjectType.SUSPENDED.name]
        )
        self.assertEqual(Project.objects.filter_active().count(), number_of_projects_to_create[ProjectType.ACTIVE.name])
        self.assertEqual(
            Project.objects.filter_completed().count(), number_of_projects_to_create[ProjectType.COMPLETED.name]
        )

    def test_that_command_should_not_create_any_project_when_any_argument_is_not_specified(self):
        management.call_command("generate_test_data")

        self.assertEqual(Project.objects.all().count(), 0)

    @parameterized.expand(
        [(ProjectType.SUSPENDED.name, 2), (ProjectType.ACTIVE.name, 2), (ProjectType.COMPLETED.name, 2)]
    )
    def test_that_command_should_not_require_all_arguments_to_create_specified_projects(
        self, project_type, number_of_projects_to_create
    ):
        management.call_command("generate_test_data", **{project_type: number_of_projects_to_create})

        self.check_number_of_projects_in_database(project_type, number_of_projects_to_create)

    @parameterized.expand(
        [
            (ProjectType.SUSPENDED.name, 0, 0),
            (ProjectType.SUSPENDED.name, -100, 0),
            (ProjectType.SUSPENDED.name, 2, 2),
            (ProjectType.ACTIVE.name, 0, 0),
            (ProjectType.ACTIVE.name, -100, 0),
            (ProjectType.ACTIVE.name, 2, 2),
            (ProjectType.COMPLETED.name, 0, 0),
            (ProjectType.COMPLETED.name, -100, 0),
            (ProjectType.COMPLETED.name, 2, 2),
        ]
    )
    def test_that_command_should_not_create_projects_when_specified_number_is_not_greater_than_0(
        self, project_type, number_of_projects_to_create, expected_number_of_projects_in_database
    ):
        management.call_command("generate_test_data", **{project_type: number_of_projects_to_create})

        self.check_number_of_projects_in_database(project_type, expected_number_of_projects_in_database)

    @parameterized.expand(
        [(ProjectType.SUSPENDED.name, 1), (ProjectType.ACTIVE.name, 1), (ProjectType.COMPLETED.name, 1)]
    )
    def test_that_despite_filled_database_command_should_create_specified_number_of_projects(
        self, project_type, number_of_projects
    ):
        management.call_command("generate_test_data", **{project_type: number_of_projects})

        management.call_command("generate_test_data", **{project_type: number_of_projects + 1})

        self.check_number_of_projects_in_database(project_type, number_of_projects + 1)

    def check_number_of_projects_in_database(self, project_type, expected_number_of_projects):
        if project_type == ProjectType.SUSPENDED.name:
            self.assertEqual(Project.objects.filter_suspended().count(), expected_number_of_projects)
        elif project_type == ProjectType.ACTIVE.name:
            self.assertEqual(Project.objects.filter_active().count(), expected_number_of_projects)
        elif project_type == ProjectType.COMPLETED.name:
            self.assertEqual(Project.objects.filter_completed().count(), expected_number_of_projects)


class CombinedOptionsTests(TestCase):
    SUPERUSER = "SUPERUSER"

    def setUp(self):
        self.number_of_admins_to_create = 1
        self.number_of_employees_to_create = 2
        self.number_of_managers_to_create = 2

        self.number_of_suspended_projects_to_create = 1
        self.number_of_active_projects_to_create = 2
        self.number_of_completed_projects_to_create = 2

        self.combined_options = {
            CustomUser.UserType.ADMIN.name: self.number_of_admins_to_create,
            CustomUser.UserType.EMPLOYEE.name: self.number_of_employees_to_create,
            CustomUser.UserType.MANAGER.name: self.number_of_managers_to_create,
            self.SUPERUSER: True,
            ProjectType.SUSPENDED.name: self.number_of_suspended_projects_to_create,
            ProjectType.ACTIVE.name: self.number_of_active_projects_to_create,
            ProjectType.COMPLETED.name: self.number_of_completed_projects_to_create,
        }

    def test_that_passing_users_arguments_should_not_affect_creating_projects(self):
        management.call_command("generate_test_data", **self.combined_options)

        self.check_number_of_all_projects_in_database()

    def test_that_passing_projects_arguments_should_not_affect_creating_users(self):
        management.call_command("generate_test_data", **self.combined_options)

        self.check_number_of_all_users_in_database()

    def test_that_result_of_passing_all_arguments_should_be_created_specified_number_of_projects_and_users(self):
        management.call_command("generate_test_data", **self.combined_options)

        self.check_number_of_all_projects_in_database()

        self.check_number_of_all_users_in_database()

    def check_number_of_all_projects_in_database(self):
        self.assertEqual(Project.objects.filter_suspended().count(), self.number_of_suspended_projects_to_create)
        self.assertEqual(Project.objects.filter_active().count(), self.number_of_active_projects_to_create)
        self.assertEqual(Project.objects.filter_completed().count(), self.number_of_completed_projects_to_create)

    def check_number_of_all_users_in_database(self):
        self.assertEqual(
            CustomUser.objects.filter(user_type=CustomUser.UserType.ADMIN.name, is_superuser=False).count(),
            self.number_of_admins_to_create,
        )
        self.assertEqual(
            CustomUser.objects.filter(user_type=CustomUser.UserType.EMPLOYEE.name).count(),
            self.number_of_employees_to_create,
        )
        self.assertEqual(
            CustomUser.objects.filter(user_type=CustomUser.UserType.MANAGER.name).count(),
            self.number_of_managers_to_create,
        )
        self.assertEqual(CustomUser.objects.filter(is_superuser=True).count(), 1)


class PassIncorrectArgumentsTests(TestCase):
    @parameterized.expand([("--admin", "test-text"), ("--employee", "test-text"), ("--manager", "test-text")])
    def test_that_passing_text_instead_of_number_for_users_arguments_should_raise_error(self, user_type, test_text):
        with self.assertRaises(CommandError):
            management.call_command("generate_test_data", f"{user_type}={test_text}")

    @parameterized.expand([("--suspended", "test-text"), ("--active", "test-text"), ("--completed", "test-text")])
    def test_that_passing_text_instead_of_number_for_projects_arguments_should_raise_error(
        self, project_type, test_text
    ):
        with self.assertRaises(CommandError):
            management.call_command("generate_test_data", f"{project_type}={test_text}")

    @parameterized.expand([(1,), ("test_text",)])
    def test_that_passing_any_value_for_positional_superuser_argument_should_raise_error(self, test_value):
        with self.assertRaises(CommandError):
            management.call_command("generate_test_data", f"--superuser={test_value}")
