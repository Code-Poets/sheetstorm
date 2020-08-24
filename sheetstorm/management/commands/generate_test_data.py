import logging
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from managers.factories import ProjectFactory
from managers.models import Project
from sheetstorm.management.commands.constants import DATA_SETS
from sheetstorm.management.commands.constants import SUPERUSER_USER_TYPE
from sheetstorm.management.commands.constants import DataSize
from sheetstorm.management.commands.constants import ProjectType
from users.factories import UserFactory
from users.models import CustomUser


class UnsupportedProjectTypeException(Exception):
    pass


class NoDataSetRequestedException(Exception):
    pass


class Command(BaseCommand):
    help = "Create initial sample data for SheetStorm application testing."

    OptionsDictType = Dict[str, Union[bool, int, None]]

    PROJECT_START_DATE_TIME_DELTA = relativedelta(months=1, day=1)
    PROJECT_STOP_DATE_TIME_DELTA = relativedelta(days=14)

    def __init__(self) -> None:
        super().__init__()
        self.number_of_admins: int
        self.number_of_employees: int
        self.number_of_managers: int
        self.number_of_suspended_projects: int
        self.number_of_active_projects: int
        self.number_of_completed_projects: int
        self.is_superuser_request: bool
        self.is_small_set_request: bool
        self.is_medium_set_request: bool
        self.is_large_set_request: bool
        self.is_extra_large_set_request: bool

    @transaction.atomic
    def handle(self, *args: Any, **options: Union[bool, int, None]) -> None:
        is_request_to_use_prepared_set = self._get_request_to_create_data_using_prepared_set(options)

        if is_request_to_use_prepared_set:
            self.create_data_using_prepared_set(options)
        else:
            self.execute_creating_users(options)
            self.execute_creating_project(options)

        logging.info(f"Total number of users in the database: {CustomUser.objects.count()}")
        logging.info(f"Total number of projects in the database: {Project.objects.count()}")

    def _get_request_to_create_data_using_prepared_set(self, options: OptionsDictType) -> Any:
        self._init_parser_parameters(options)

        return any(
            [
                self.is_small_set_request,
                self.is_medium_set_request,
                self.is_large_set_request,
                self.is_extra_large_set_request,
            ]
        )

    def create_data_using_prepared_set(self, options: OptionsDictType) -> None:
        requested_set = self._pick_dataset_to_create(options)

        self.execute_creating_users(requested_set)
        self.execute_creating_project(requested_set)

    def _pick_dataset_to_create(self, options: OptionsDictType) -> Any:
        self._init_parser_parameters(options)

        if self.is_small_set_request:
            requested_set = DATA_SETS[DataSize.SMALL.name]
        elif self.is_medium_set_request:
            requested_set = DATA_SETS[DataSize.MEDIUM.name]
        elif self.is_large_set_request:
            requested_set = DATA_SETS[DataSize.LARGE.name]
        elif self.is_extra_large_set_request:
            requested_set = DATA_SETS[DataSize.EXTRA_LARGE.name]
        else:
            raise NoDataSetRequestedException("No data set requested")

        return requested_set

    def execute_creating_users(self, options: OptionsDictType) -> None:
        user_options = self._get_user_options(options)
        is_need_to_create_superuser = self._get_superuser_request(options)

        for (user_type, number_of_users) in user_options.items():
            if number_of_users is not None:
                self.create_user(user_type, number_of_users)

        if is_need_to_create_superuser:
            self.create_user(SUPERUSER_USER_TYPE)

    @staticmethod
    def _get_user_options(options: OptionsDictType) -> Dict[str, Optional[int]]:
        return {
            CustomUser.UserType.ADMIN.name: options[CustomUser.UserType.ADMIN.name],
            CustomUser.UserType.EMPLOYEE.name: options[CustomUser.UserType.EMPLOYEE.name],
            CustomUser.UserType.MANAGER.name: options[CustomUser.UserType.MANAGER.name],
        }

    @staticmethod
    def _get_superuser_request(options: Dict[str, Any]) -> bool:
        is_superuser_create_request = options[SUPERUSER_USER_TYPE]
        is_superuser_in_database = CustomUser.objects.filter(is_superuser=True).exists()

        return is_superuser_create_request and not is_superuser_in_database

    def create_user(self, user_type: str, number_of_users_to_create: int = 1) -> None:
        factory_parameters = self._set_user_factory_parameters(user_type)

        for user_number in range(number_of_users_to_create):
            user_email = f"user.{user_type}{user_number + 1}@codepoets.it".lower()

            if not CustomUser.objects.filter(email=user_email).exists():
                logging.info(f"{number_of_users_to_create - user_number} {user_type}(s) left to create")
                UserFactory(**factory_parameters, email=user_email)

    @staticmethod
    def _set_user_factory_parameters(user_type: str) -> Dict[str, Union[str, bool]]:
        return {
            "user_type": CustomUser.UserType.ADMIN.name if user_type == SUPERUSER_USER_TYPE else user_type,
            "is_staff": user_type in (CustomUser.UserType.ADMIN.name, SUPERUSER_USER_TYPE),
            "is_superuser": user_type == SUPERUSER_USER_TYPE,
        }

    def execute_creating_project(self, options: OptionsDictType) -> None:
        projects_to_create = self._set_number_of_projects_to_create(options)

        for (project_type, number_of_projects) in projects_to_create.items():
            self.create_project(project_type, number_of_projects)

    def _set_number_of_projects_to_create(self, options: OptionsDictType) -> Dict[str, int]:
        return {
            ProjectType.SUSPENDED.name: self._compute_number_of_projects_to_create(options, ProjectType.SUSPENDED.name),
            ProjectType.ACTIVE.name: self._compute_number_of_projects_to_create(options, ProjectType.ACTIVE.name),
            ProjectType.COMPLETED.name: self._compute_number_of_projects_to_create(options, ProjectType.COMPLETED.name),
        }

    @staticmethod
    def _compute_number_of_projects_to_create(options: OptionsDictType, project_type: str) -> int:
        if project_type == ProjectType.SUSPENDED.name:
            number_of_projects_in_database = Project.objects.filter_suspended().count()
        elif project_type == ProjectType.ACTIVE.name:
            number_of_projects_in_database = Project.objects.filter_active().count()
        elif project_type == ProjectType.COMPLETED.name:
            number_of_projects_in_database = Project.objects.filter_completed().count()
        else:
            raise UnsupportedProjectTypeException(f"{project_type} project type do not exist")

        return options[project_type] - number_of_projects_in_database if options[project_type] is not None else 0

    def create_project(self, project_type: str, number_of_projects_to_create: int) -> None:
        factory_parameters = self._set_project_factory_parameters(project_type)

        for project_number in range(number_of_projects_to_create):
            logging.info(f"{number_of_projects_to_create - project_number} {project_type} project(s) left to create")
            ProjectFactory(**factory_parameters)

    def _set_project_factory_parameters(self, project_type: str) -> Dict[str, Union[timezone.datetime, bool]]:
        return {
            "start_date": self._create_start_date(),
            "suspended": project_type == ProjectType.SUSPENDED.name,
            "stop_date": self._create_stop_date() if project_type == ProjectType.COMPLETED.name else None,
        }

    @staticmethod
    def _create_start_date(time_delta: Any = PROJECT_START_DATE_TIME_DELTA) -> timezone.datetime:
        return timezone.now() - time_delta

    @staticmethod
    def _create_stop_date(time_delta: Any = PROJECT_STOP_DATE_TIME_DELTA) -> timezone.datetime:
        return timezone.now() - time_delta

    def add_arguments(self, parser: Any) -> None:
        data_size_arguments = parser.add_mutually_exclusive_group()

        parser.add_argument(
            "-a",
            "--admin",
            dest=CustomUser.UserType.ADMIN.name,
            type=int,
            help="Indicates the maximum number of admins to be in the database",
        )
        parser.add_argument(
            "-e",
            "--employee",
            dest=CustomUser.UserType.EMPLOYEE.name,
            type=int,
            help="Indicates the maximum number of employees to be in the database",
        )
        parser.add_argument(
            "-m",
            "--manager",
            dest=CustomUser.UserType.MANAGER.name,
            type=int,
            help="Indicates the maximum number of managers to be in the database",
        )
        parser.add_argument(
            "-s",
            "--superuser",
            dest=SUPERUSER_USER_TYPE,
            action="store_true",
            help="Create and add superuser to the database if there isn't one",
        )
        parser.add_argument(
            "-su",
            "--suspended",
            dest=ProjectType.SUSPENDED.name,
            type=int,
            help="Indicates the maximum number of suspended projects to be in the database",
        )
        parser.add_argument(
            "-ac",
            "--active",
            dest=ProjectType.ACTIVE.name,
            type=int,
            help="Indicates the maximum number of active projects to be in the database",
        )
        parser.add_argument(
            "-co",
            "--completed",
            dest=ProjectType.COMPLETED.name,
            type=int,
            help="Indicates the maximum number of completed projects to be in the database",
        )
        data_size_arguments.add_argument(
            "--small",
            dest=DataSize.SMALL.name,
            action="store_true",
            help="Use prepared small set to generate test data",
        )
        data_size_arguments.add_argument(
            "--medium",
            dest=DataSize.MEDIUM.name,
            action="store_true",
            help="Use prepared medium set to generate test data",
        )
        data_size_arguments.add_argument(
            "--large",
            dest=DataSize.LARGE.name,
            action="store_true",
            help="Use prepared large set to generate test data",
        )
        data_size_arguments.add_argument(
            "--extra-large",
            dest=DataSize.EXTRA_LARGE.name,
            action="store_true",
            help="Use prepared extra large set to generate test data",
        )

    def _init_parser_parameters(self, options: Any) -> None:
        self.number_of_admins = options[CustomUser.UserType.ADMIN.name]
        self.number_of_employees = options[CustomUser.UserType.EMPLOYEE.name]
        self.number_of_managers = options[CustomUser.UserType.MANAGER.name]
        self.number_of_suspended_projects = options[ProjectType.SUSPENDED.name]
        self.number_of_active_projects = options[ProjectType.ACTIVE.name]
        self.number_of_completed_projects = options[ProjectType.COMPLETED.name]
        self.is_superuser_request = options[SUPERUSER_USER_TYPE]
        self.is_small_set_request = options[DataSize.SMALL.name]
        self.is_medium_set_request = options[DataSize.MEDIUM.name]
        self.is_large_set_request = options[DataSize.LARGE.name]
        self.is_extra_large_set_request = options[DataSize.EXTRA_LARGE.name]
