from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.utils import timezone
from parameterized import parameterized

from managers.factories import ProjectFactory
from managers.models import Project
from sheetstorm.management.commands.constants import DATA_SETS
from sheetstorm.management.commands.constants import SUPERUSER_USER_TYPE
from sheetstorm.management.commands.constants import DataSize
from sheetstorm.management.commands.generate_test_data import Command as GenerateTestDataCommand
from sheetstorm.management.commands.generate_test_data import NoDataSetRequestedException
from sheetstorm.management.commands.generate_test_data import ProjectType
from sheetstorm.management.commands.generate_test_data import UnsupportedProjectTypeException
from users.factories import UserFactory
from users.models import CustomUser


class CreateUserMethodsTests(TestCase):
    def test_get_users_options_function_should_return_only_users_options(self):
        GenerateTestDataCommand.number_of_active_projects = 2
        GenerateTestDataCommand.some_test_parameter = None
        GenerateTestDataCommand.number_of_admins = 2
        GenerateTestDataCommand.number_of_employees = None
        GenerateTestDataCommand.number_of_managers = 2

        expected_options = {
            CustomUser.UserType.ADMIN.name: 2,
            CustomUser.UserType.EMPLOYEE.name: None,
            CustomUser.UserType.MANAGER.name: 2,
        }

        GenerateTestDataCommand.is_superuser_request = True

        self.assertEqual(GenerateTestDataCommand()._get_user_options(), expected_options)

    def test_get_superuser_request_function_should_return_true_if_there_is_superuser_request(self):
        GenerateTestDataCommand.is_superuser_request = True

        self.assertTrue(GenerateTestDataCommand()._get_superuser_request())

    def test_get_superuser_request_function_should_return_false_if_there_is_no_superuser_request(self):
        GenerateTestDataCommand.is_superuser_request = False

        self.assertFalse(GenerateTestDataCommand()._get_superuser_request())

    def test_get_superuser_request_function_should_return_false_if_superuser_already_exists(self):
        UserFactory(is_superuser=True)

        GenerateTestDataCommand.is_superuser_request = True

        self.assertFalse(GenerateTestDataCommand()._get_superuser_request())

    @parameterized.expand([CustomUser.UserType.ADMIN.name, SUPERUSER_USER_TYPE])
    def test_admin_and_superuser_should_have_staff_property(self, user_type):
        self.assertTrue(GenerateTestDataCommand._set_user_factory_parameters(user_type).get("is_staff"))

    @parameterized.expand([CustomUser.UserType.EMPLOYEE.name, CustomUser.UserType.MANAGER.name])
    def test_employee_and_manager_should_not_have_staff_property(self, user_type):
        self.assertFalse(GenerateTestDataCommand._set_user_factory_parameters(user_type).get("is_staff"))

    @parameterized.expand(
        [CustomUser.UserType.ADMIN.name, CustomUser.UserType.EMPLOYEE.name, CustomUser.UserType.MANAGER.name]
    )
    def test_any_user_should_not_have_superuser_property_except_superuser(self, user_type):
        self.assertFalse(GenerateTestDataCommand._set_user_factory_parameters(user_type).get("is_superuser"))

    def test_superuser_should_have_superuser_property(self):
        self.assertTrue(GenerateTestDataCommand._set_user_factory_parameters(SUPERUSER_USER_TYPE).get("is_superuser"))

    @parameterized.expand([CustomUser.UserType.ADMIN.name, SUPERUSER_USER_TYPE])
    def test_admin_and_superuser_should_have_user_type_coded_as_admin(self, user_type):
        self.assertEqual(
            GenerateTestDataCommand._set_user_factory_parameters(user_type).get("user_type"),
            CustomUser.UserType.ADMIN.name,
        )

    @parameterized.expand([CustomUser.UserType.EMPLOYEE.name, CustomUser.UserType.MANAGER.name])
    def test_employee_and_manager_should_have_user_type_coded_as_based_of_user_type_name(self, user_type):
        self.assertEqual(GenerateTestDataCommand._set_user_factory_parameters(user_type).get("user_type"), user_type)

    @parameterized.expand(
        [
            (CustomUser.UserType.ADMIN.name, 2),
            (CustomUser.UserType.EMPLOYEE.name, 5),
            (CustomUser.UserType.MANAGER.name, 3),
        ]
    )
    def test_result_of_create_user_function_should_be_specified_number_of_users_in_database(
        self, user_type, number_of_users_to_create
    ):
        GenerateTestDataCommand().create_user(user_type, number_of_users_to_create)

        self.assertEqual(CustomUser.objects.filter(user_type=user_type).count(), number_of_users_to_create)

    @parameterized.expand(
        [
            (CustomUser.UserType.ADMIN.name, 3),
            (CustomUser.UserType.EMPLOYEE.name, 3),
            (CustomUser.UserType.MANAGER.name, 3),
        ]
    )
    def test_despite_filled_database_result_of_create_user_function_should_be_specified_number_of_users_in_database(
        self, user_type, number_of_users_to_create
    ):
        mock_number_of_users_in_database_less_than_next_request = 2
        self._generate_test_users(mock_number_of_users_in_database_less_than_next_request, user_type)

        GenerateTestDataCommand().create_user(user_type, number_of_users_to_create)

        self.assertEqual(CustomUser.objects.filter(user_type=user_type).count(), number_of_users_to_create)

    @parameterized.expand(
        [
            (CustomUser.UserType.ADMIN.name, 0),
            (CustomUser.UserType.ADMIN.name, 3),
            (CustomUser.UserType.EMPLOYEE.name, 0),
            (CustomUser.UserType.EMPLOYEE.name, 3),
            (CustomUser.UserType.MANAGER.name, 0),
            (CustomUser.UserType.MANAGER.name, 3),
        ]
    )
    def test_create_user_function_should_not_create_users_if_number_in_database_is_greater_than_or_equal_to_specified(
        self, user_type, number_of_users_to_subtract_from_existing
    ):
        mock_number_of_users_to_create = 2
        users = self._generate_test_users(mock_number_of_users_to_create, user_type)

        GenerateTestDataCommand().create_user(user_type, len(users) - number_of_users_to_subtract_from_existing)

        self.assertEqual(CustomUser.objects.filter(user_type=user_type).count(), mock_number_of_users_to_create)

    def test_result_of_execute_creating_users_function_should_be_specified_number_of_users_in_database(self):
        GenerateTestDataCommand.number_of_admins = 1
        GenerateTestDataCommand.number_of_managers = None
        GenerateTestDataCommand.number_of_employees = 2
        GenerateTestDataCommand.is_superuser_request = True
        GenerateTestDataCommand().execute_creating_users()

        self.assertEqual(
            CustomUser.objects.filter(user_type=CustomUser.UserType.ADMIN.name, is_superuser=False).count(), 1
        )
        self.assertEqual(CustomUser.objects.filter(user_type=CustomUser.UserType.EMPLOYEE.name).count(), 2)
        self.assertEqual(CustomUser.objects.filter(user_type=CustomUser.UserType.MANAGER.name).count(), 0)
        self.assertEqual(CustomUser.objects.filter(is_superuser=True).count(), 1)

    def test_despite_filled_database_result_of_execute_function_should_be_specified_number_of_users_in_database(self):
        mock_number_of_users_to_create = 1
        self._generate_test_users(mock_number_of_users_to_create, CustomUser.UserType.ADMIN.name)
        self._generate_test_users(mock_number_of_users_to_create, CustomUser.UserType.EMPLOYEE.name)
        self._generate_test_users(mock_number_of_users_to_create, CustomUser.UserType.MANAGER.name)

        GenerateTestDataCommand.number_of_admins = 2
        GenerateTestDataCommand.number_of_managers = 2
        GenerateTestDataCommand.number_of_employees = 2
        GenerateTestDataCommand.is_superuser_request = False

        GenerateTestDataCommand().execute_creating_users()

        self.assertEqual(
            CustomUser.objects.filter(user_type=CustomUser.UserType.ADMIN.name, is_superuser=False).count(), 2
        )
        self.assertEqual(CustomUser.objects.filter(user_type=CustomUser.UserType.EMPLOYEE.name).count(), 2)
        self.assertEqual(CustomUser.objects.filter(user_type=CustomUser.UserType.MANAGER.name).count(), 2)

    @staticmethod
    def _generate_test_users(number_of_users_to_fill_database, user_type):
        user_list = []

        for user_number in range(number_of_users_to_fill_database):
            user_list.append(
                UserFactory(email=f"user.{user_type}{user_number + 1}@codepoets.it".lower(), user_type=user_type)
            )

        return user_list


class CreateProjectMethodsTests(TestCase):
    def setUp(self):
        self.mock_number_of_suspended_projects_to_create = 4
        self.mock_number_of_active_projects_to_create = 5
        self.mock_number_of_completed_projects_to_create = 7

        self.options = {
            ProjectType.SUSPENDED.name: self.mock_number_of_suspended_projects_to_create,
            ProjectType.ACTIVE.name: self.mock_number_of_active_projects_to_create,
            ProjectType.COMPLETED.name: self.mock_number_of_completed_projects_to_create,
        }

        GenerateTestDataCommand.number_of_suspended_projects = self.mock_number_of_suspended_projects_to_create
        GenerateTestDataCommand.number_of_active_projects = self.mock_number_of_active_projects_to_create
        GenerateTestDataCommand.number_of_completed_projects = self.mock_number_of_completed_projects_to_create

    @parameterized.expand(
        [(ProjectType.SUSPENDED.name, 2), (ProjectType.ACTIVE.name, 3), (ProjectType.COMPLETED.name, 5)]
    )
    def test_number_of_projects_to_create_should_be_a_difference_of_number_of_projects_in_database_and_defined_number(
        self, project_type, expected_result
    ):
        self._generate_test_projects(number_of_projects_to_fill_database=2, project_type=project_type)

        self.assertEqual(GenerateTestDataCommand()._compute_number_of_projects_to_create(project_type), expected_result)

    def test_compute_number_of_projects_to_create_function_should_raise_error_if_project_type_does_not_exist(self):
        with self.assertRaises(UnsupportedProjectTypeException):
            GenerateTestDataCommand()._compute_number_of_projects_to_create("error")

    @parameterized.expand([ProjectType.SUSPENDED.name, ProjectType.ACTIVE.name, ProjectType.COMPLETED.name])
    def test_compute_number_of_projects_to_create_function_should_return_0_if_number_of_projects_is_not_specified(
        self, project_type
    ):
        GenerateTestDataCommand.number_of_suspended_projects = None
        GenerateTestDataCommand.number_of_active_projects = None
        GenerateTestDataCommand.number_of_completed_projects = None

        self.assertEqual(GenerateTestDataCommand()._compute_number_of_projects_to_create(project_type), 0)

    def test_number_of_projects_to_create_should_be_set_and_equal_to_computed_number(self):
        suspended_projects = self._generate_test_projects(
            number_of_projects_to_fill_database=2, project_type=ProjectType.SUSPENDED.name
        )
        active_projects = self._generate_test_projects(
            number_of_projects_to_fill_database=2, project_type=ProjectType.ACTIVE.name
        )
        completed_projects = self._generate_test_projects(
            number_of_projects_to_fill_database=2, project_type=ProjectType.COMPLETED.name
        )

        expected_options = {
            ProjectType.ACTIVE.name: self._compute_number_of_projects(
                self.options, active_projects, ProjectType.ACTIVE.name
            ),
            ProjectType.SUSPENDED.name: self._compute_number_of_projects(
                self.options, suspended_projects, ProjectType.SUSPENDED.name
            ),
            ProjectType.COMPLETED.name: self._compute_number_of_projects(
                self.options, completed_projects, ProjectType.COMPLETED.name
            ),
        }

        self.assertEqual(GenerateTestDataCommand()._set_number_of_projects_to_create(), expected_options)

    def test_start_date_should_be_of_datetime_type_and_set_in_past(self):
        start_date_returned_by_function = GenerateTestDataCommand._create_start_date()

        self.assertIsInstance(start_date_returned_by_function, timezone.datetime)
        self.assertLess(start_date_returned_by_function, timezone.now())

    def test_stop_date_should_be_of_datetime_type_and_set_in_past(self):
        stop_date_returned_by_function = GenerateTestDataCommand._create_stop_date()

        self.assertIsInstance(stop_date_returned_by_function, timezone.datetime)
        self.assertLess(stop_date_returned_by_function, timezone.now())

    def test_suspended_projects_should_have_suspended_property(self):
        self.assertTrue(
            GenerateTestDataCommand()._set_project_factory_parameters(ProjectType.SUSPENDED.name).get("suspended")
        )

    @parameterized.expand([ProjectType.ACTIVE.name, ProjectType.COMPLETED.name])
    def test_active_and_completed_projects_should_not_have_suspended_property(self, project_type):
        self.assertFalse(GenerateTestDataCommand()._set_project_factory_parameters(project_type).get("suspended"))

    def test_completed_projects_should_have_stop_date(self):
        self.assertIsNotNone(
            GenerateTestDataCommand()._set_project_factory_parameters(ProjectType.COMPLETED.name).get("stop_date")
        )

    @parameterized.expand([ProjectType.SUSPENDED.name, ProjectType.ACTIVE.name])
    def test_active_and_suspended_projects_should_not_have_stop_date(self, project_type):
        self.assertIsNone(GenerateTestDataCommand()._set_project_factory_parameters(project_type).get("stop_date"))

    @parameterized.expand([ProjectType.SUSPENDED.name, ProjectType.ACTIVE.name, ProjectType.COMPLETED.name])
    def test_any_project_should_have_start_date(self, project_type):
        self.assertIsNotNone(GenerateTestDataCommand()._set_project_factory_parameters(project_type).get("start_date"))

    def test_result_of_execute_function_should_be_specified_number_of_projects_in_database(self):
        GenerateTestDataCommand().execute_creating_project()

        self.assertEqual(Project.objects.filter_completed().count(), self.mock_number_of_completed_projects_to_create)
        self.assertEqual(Project.objects.filter_active().count(), self.mock_number_of_active_projects_to_create)
        self.assertEqual(Project.objects.filter_suspended().count(), self.mock_number_of_suspended_projects_to_create)

    def test_create_project_function_should_create_computed_number_of_suspended_projects(self):
        suspended_projects = self._generate_test_projects(2, ProjectType.SUSPENDED.name)

        number_of_projects_to_create = self._compute_number_of_projects(
            self.options, suspended_projects, ProjectType.SUSPENDED.name
        )

        GenerateTestDataCommand().create_project(ProjectType.SUSPENDED.name, number_of_projects_to_create)

        self.assertEqual(
            Project.objects.filter_suspended().count(), len(suspended_projects) + number_of_projects_to_create
        )

    def test_create_project_function_should_create_computed_number_of_active_projects(self):
        active_projects = self._generate_test_projects(2, ProjectType.ACTIVE.name)

        number_of_projects_to_create = self._compute_number_of_projects(
            self.options, active_projects, ProjectType.ACTIVE.name
        )

        GenerateTestDataCommand().create_project(ProjectType.ACTIVE.name, number_of_projects_to_create)

        self.assertEqual(Project.objects.filter_active().count(), len(active_projects) + number_of_projects_to_create)

    def test_create_project_function_should_create_computed_number_of_completed_projects(self):
        completed_projects = self._generate_test_projects(2, ProjectType.COMPLETED.name)

        number_of_projects_to_create = self._compute_number_of_projects(
            self.options, completed_projects, ProjectType.COMPLETED.name
        )

        GenerateTestDataCommand().create_project(ProjectType.COMPLETED.name, number_of_projects_to_create)

        self.assertEqual(
            Project.objects.filter_completed().count(), len(completed_projects) + number_of_projects_to_create
        )

    @parameterized.expand([(0,), (3,)])
    def test_projects_should_not_be_created_if_number_of_projects_in_database_is_greater_than_or_equal_to_specified(
        self, number_of_projects_to_subtract_from_existing
    ):
        suspended_projects = self._generate_test_projects(
            number_of_projects_to_fill_database=2, project_type=ProjectType.SUSPENDED.name
        )
        active_projects = self._generate_test_projects(
            number_of_projects_to_fill_database=2, project_type=ProjectType.ACTIVE.name
        )
        completed_projects = self._generate_test_projects(
            number_of_projects_to_fill_database=2, project_type=ProjectType.COMPLETED.name
        )

        GenerateTestDataCommand.number_of_suspended_projects = (
            len(suspended_projects) - number_of_projects_to_subtract_from_existing
        )
        GenerateTestDataCommand.number_of_active_projects = (
            len(active_projects) - number_of_projects_to_subtract_from_existing
        )
        GenerateTestDataCommand.number_of_completed_projects = (
            len(completed_projects) - number_of_projects_to_subtract_from_existing
        )

        GenerateTestDataCommand().execute_creating_project()

        self.assertEqual(Project.objects.filter_suspended().count(), len(suspended_projects))
        self.assertEqual(Project.objects.filter_active().count(), len(active_projects))
        self.assertEqual(Project.objects.filter_completed().count(), len(completed_projects))

    @staticmethod
    def _generate_test_projects(number_of_projects_to_fill_database, project_type):
        project_list = []

        for _ in range(number_of_projects_to_fill_database):
            if project_type == ProjectType.SUSPENDED.name:
                project = ProjectFactory(suspended=True)
            elif project_type == ProjectType.ACTIVE.name:
                project = ProjectFactory()
            elif project_type == ProjectType.COMPLETED.name:
                project = ProjectFactory(stop_date=timezone.now() - relativedelta(days=1))
            else:
                raise UnsupportedProjectTypeException
            project_list.append(project)

        return project_list

    @staticmethod
    def _compute_number_of_projects(options, projects_in_database, project_type):
        if project_type == ProjectType.SUSPENDED.name:
            number_of_projects_to_create = options[ProjectType.SUSPENDED.name] - len(projects_in_database)
        elif project_type == ProjectType.ACTIVE.name:
            number_of_projects_to_create = options[ProjectType.ACTIVE.name] - len(projects_in_database)
        elif project_type == ProjectType.COMPLETED.name:
            number_of_projects_to_create = options[ProjectType.COMPLETED.name] - len(projects_in_database)
        else:
            raise UnsupportedProjectTypeException

        return number_of_projects_to_create


class CreateDataFromPreparedSetTests(TestCase):
    def setUp(self) -> None:
        GenerateTestDataCommand.is_small_set_request = False
        GenerateTestDataCommand.is_medium_set_request = False
        GenerateTestDataCommand.is_large_set_request = False
        GenerateTestDataCommand.is_extra_large_set_request = False

    def test_get_request_to_create_data_using_prepared_set_function_should_return_true_if_any_set_requested(self):
        GenerateTestDataCommand.is_small_set_request = True

        self.assertTrue(GenerateTestDataCommand()._get_request_to_create_data_using_prepared_set())

    def test_get_request_to_create_data_using_prepared_set_function_should_return_false_if_parameters_are_not_provided(
        self
    ):
        self.assertFalse(GenerateTestDataCommand()._get_request_to_create_data_using_prepared_set())

    @parameterized.expand(
        [
            (True, False, False, False, DataSize.SMALL.name),
            (False, True, False, False, DataSize.MEDIUM.name),
            (False, False, True, False, DataSize.LARGE.name),
            (False, False, False, True, DataSize.EXTRA_LARGE.name),
        ]
    )
    def test_pick_dataset_to_create_function_should_return_one_specified_set_if_there_is_request(
        self, small_requested, medium_requested, large_requested, extra_large_requested, set_name
    ):
        GenerateTestDataCommand.is_small_set_request = small_requested
        GenerateTestDataCommand.is_medium_set_request = medium_requested
        GenerateTestDataCommand.is_large_set_request = large_requested
        GenerateTestDataCommand.is_extra_large_set_request = extra_large_requested

        self.assertEqual(GenerateTestDataCommand()._pick_dataset_to_create(), DATA_SETS[set_name])

    def test_pick_dataset_to_create_function_should_raise_error_if_there_is_no_request_for_any(self):
        with self.assertRaises(NoDataSetRequestedException):
            GenerateTestDataCommand()._pick_dataset_to_create()
