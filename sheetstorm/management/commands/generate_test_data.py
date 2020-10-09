import logging
import random
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from managers.factories import ProjectFactory
from managers.models import Project
from sheetstorm.management.commands.constants import DATA_SETS
from sheetstorm.management.commands.constants import DATA_SIZE_PARAMETER
from sheetstorm.management.commands.constants import SUPERUSER_USER_TYPE
from sheetstorm.management.commands.constants import DataSize
from sheetstorm.management.commands.constants import ProjectType
from sheetstorm.management.commands.constants import UsersInProjects
from users.factories import UserFactory
from users.models import CustomUser


class UnsupportedProjectTypeException(Exception):
    pass


class NoDataSetRequestedException(Exception):
    pass


class Command(BaseCommand):
    help = "Create initial sample data for SheetStorm application testing."

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
        self.data_set_size: Any

        self.max_number_of_admins_in_suspended_project: int
        self.max_number_of_employees_in_suspended_project: int
        self.max_number_of_managers_in_suspended_project: int
        self.max_number_of_admins_in_active_project: int
        self.max_number_of_employees_in_active_project: int
        self.max_number_of_managers_in_active_project: int
        self.max_number_of_admins_in_completed_project: int
        self.max_number_of_employees_in_completed_project: int
        self.max_number_of_managers_in_completed_project: int

        self.employees_list: List
        self.admins_list: List
        self.managers_list: List
        self.active_projects_list: List
        self.suspended_projects_list: List
        self.completed_projects_list: List

    @transaction.atomic
    def handle(self, *args: Any, **options: Union[bool, int, None]) -> None:
        self._init_values_from_given_options(options)

        self.execute_creating_users()
        self.execute_creating_project()

        self._get_list_of_created_users_and_projects()

        is_adding_users_to_projects_possible = self._get_request_to_create_data_using_prepared_set()

        if is_adding_users_to_projects_possible:
            self.execute_adding_users_to_projects()
        else:
            logging.info("Adding users to projects not supported")

        logging.info(f"Total number of users in the database: {CustomUser.objects.count()}")
        logging.info(f"Total number of projects in the database: {Project.objects.count()}")

    def _init_values_from_given_options(self, options: Dict[str, Any]) -> None:
        self.data_set_size = options[DATA_SIZE_PARAMETER]

        if self._get_request_to_create_data_using_prepared_set():
            options = self._pick_dataset_to_create()

            self.max_number_of_admins_in_suspended_project = options[UsersInProjects.ADMIN_SUSPENDED.name]
            self.max_number_of_employees_in_suspended_project = options[UsersInProjects.EMPLOYEE_SUSPENDED.name]
            self.max_number_of_managers_in_suspended_project = options[UsersInProjects.MANAGER_SUSPENDED.name]
            self.max_number_of_admins_in_active_project = options[UsersInProjects.ADMIN_ACTIVE.name]
            self.max_number_of_employees_in_active_project = options[UsersInProjects.EMPLOYEE_ACTIVE.name]
            self.max_number_of_managers_in_active_project = options[UsersInProjects.MANAGER_ACTIVE.name]
            self.max_number_of_admins_in_completed_project = options[UsersInProjects.ADMIN_COMPLETED.name]
            self.max_number_of_employees_in_completed_project = options[UsersInProjects.EMPLOYEE_COMPLETED.name]
            self.max_number_of_managers_in_completed_project = options[UsersInProjects.MANAGER_COMPLETED.name]

        self.number_of_admins = options[CustomUser.UserType.ADMIN.name]
        self.number_of_employees = options[CustomUser.UserType.EMPLOYEE.name]
        self.number_of_managers = options[CustomUser.UserType.MANAGER.name]
        self.number_of_suspended_projects = options[ProjectType.SUSPENDED.name]
        self.number_of_active_projects = options[ProjectType.ACTIVE.name]
        self.number_of_completed_projects = options[ProjectType.COMPLETED.name]
        self.is_superuser_request = options[SUPERUSER_USER_TYPE]

    def _get_list_of_created_users_and_projects(self) -> None:
        self.employees_list = self._get_list_of_users(CustomUser.UserType.EMPLOYEE.name)
        self.admins_list = self._get_list_of_users(CustomUser.UserType.ADMIN.name)
        self.managers_list = self._get_list_of_users(CustomUser.UserType.MANAGER.name)

        self.active_projects_list = self._get_list_of_projects(ProjectType.ACTIVE.name)
        self.suspended_projects_list = self._get_list_of_projects(ProjectType.SUSPENDED.name)
        self.completed_projects_list = self._get_list_of_projects(ProjectType.COMPLETED.name)

    def _get_request_to_create_data_using_prepared_set(self) -> bool:
        return isinstance(self.data_set_size, str)

    def _pick_dataset_to_create(self) -> Any:
        return DATA_SETS.get(self.data_set_size)

    def execute_creating_users(self) -> None:
        user_options = self._get_user_options()
        is_need_to_create_superuser = self._get_superuser_request()

        for (user_type, number_of_users) in user_options.items():
            if number_of_users is not None:
                self.create_user(user_type, number_of_users)

        if is_need_to_create_superuser:
            self.create_user(SUPERUSER_USER_TYPE)

    def _get_user_options(self) -> Dict[str, Optional[int]]:
        return {
            CustomUser.UserType.ADMIN.name: self.number_of_admins,
            CustomUser.UserType.EMPLOYEE.name: self.number_of_employees,
            CustomUser.UserType.MANAGER.name: self.number_of_managers,
        }

    def _get_superuser_request(self) -> bool:
        is_superuser_in_database = CustomUser.objects.filter(is_superuser=True).exists()

        return self.is_superuser_request and not is_superuser_in_database

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

    def execute_creating_project(self) -> None:
        projects_to_create = self._set_number_of_projects_to_create()

        for (project_type, number_of_projects) in projects_to_create.items():
            self.create_project(project_type, number_of_projects)

    def _set_number_of_projects_to_create(self) -> Dict[str, int]:
        return {
            ProjectType.SUSPENDED.name: self._compute_number_of_projects_to_create(ProjectType.SUSPENDED.name),
            ProjectType.ACTIVE.name: self._compute_number_of_projects_to_create(ProjectType.ACTIVE.name),
            ProjectType.COMPLETED.name: self._compute_number_of_projects_to_create(ProjectType.COMPLETED.name),
        }

    def _compute_number_of_projects_to_create(self, project_type: str) -> int:
        if project_type == ProjectType.SUSPENDED.name:
            number_of_projects_in_database = Project.objects.filter_suspended().count()
            requested_number_of_projects = self.number_of_suspended_projects
        elif project_type == ProjectType.ACTIVE.name:
            number_of_projects_in_database = Project.objects.filter_active().count()
            requested_number_of_projects = self.number_of_active_projects
        elif project_type == ProjectType.COMPLETED.name:
            number_of_projects_in_database = Project.objects.filter_completed().count()
            requested_number_of_projects = self.number_of_completed_projects
        else:
            raise UnsupportedProjectTypeException("Unsupported project type")

        return (
            requested_number_of_projects - number_of_projects_in_database
            if requested_number_of_projects is not None
            else 0
        )

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

    def execute_adding_users_to_projects(self) -> None:
        self.add_users_to_projects(
            self.employees_list,
            self.suspended_projects_list,
            CustomUser.UserType.EMPLOYEE.name,
            ProjectType.SUSPENDED.name,
            self.max_number_of_employees_in_suspended_project,
        )
        self.add_users_to_projects(
            self.employees_list,
            self.active_projects_list,
            CustomUser.UserType.EMPLOYEE.name,
            ProjectType.ACTIVE.name,
            self.max_number_of_employees_in_active_project,
        )
        self.add_users_to_projects(
            self.employees_list,
            self.completed_projects_list,
            CustomUser.UserType.EMPLOYEE.name,
            ProjectType.COMPLETED.name,
            self.max_number_of_employees_in_completed_project,
        )

        self.add_users_to_projects(
            self.admins_list,
            self.suspended_projects_list,
            CustomUser.UserType.ADMIN.name,
            ProjectType.SUSPENDED.name,
            self.max_number_of_admins_in_suspended_project,
        )
        self.add_users_to_projects(
            self.admins_list,
            self.active_projects_list,
            CustomUser.UserType.ADMIN.name,
            ProjectType.ACTIVE.name,
            self.max_number_of_admins_in_active_project,
        )
        self.add_users_to_projects(
            self.admins_list,
            self.completed_projects_list,
            CustomUser.UserType.ADMIN.name,
            ProjectType.COMPLETED.name,
            self.max_number_of_admins_in_completed_project,
        )

        self.add_users_to_projects(
            self.managers_list,
            self.suspended_projects_list,
            CustomUser.UserType.MANAGER.name,
            ProjectType.SUSPENDED.name,
            self.max_number_of_managers_in_suspended_project,
            as_manager=True,
        )
        self.add_users_to_projects(
            self.managers_list,
            self.active_projects_list,
            CustomUser.UserType.MANAGER.name,
            ProjectType.ACTIVE.name,
            self.max_number_of_managers_in_active_project,
            as_manager=True,
        )
        self.add_users_to_projects(
            self.managers_list,
            self.completed_projects_list,
            CustomUser.UserType.MANAGER.name,
            ProjectType.COMPLETED.name,
            self.max_number_of_managers_in_completed_project,
            as_manager=True,
        )

        self.remove_all_random_user_projects(CustomUser.UserType.EMPLOYEE.name)
        self.remove_all_random_user_projects(CustomUser.UserType.ADMIN.name)
        self.remove_all_random_user_projects(CustomUser.UserType.MANAGER.name)

    def add_users_to_projects(
        self,
        users_list: List,
        projects_list: List,
        user_type: str,
        project_type: str,
        max_number_of_users_in_projects: int,
        as_manager: bool = False,
    ) -> None:

        for project in projects_list:
            number_of_users_to_pick = random.randint(0, max_number_of_users_in_projects)
            users_to_add_to_project = random.sample(users_list, number_of_users_to_pick)

            self.add_specified_users_to_project(project, users_to_add_to_project, as_manager)

        logging.info(f"Successfully added {user_type.lower()}s to {project_type.lower()} projects")

    @staticmethod
    def _get_list_of_users(user_type: str, is_superuser: bool = False) -> List[Any]:
        return list(CustomUser.objects.filter(user_type=user_type, is_superuser=is_superuser).all())

    @staticmethod
    def _get_list_of_projects(project_type: str) -> List[Any]:
        if project_type == ProjectType.ACTIVE.name:
            projects_list = list(Project.objects.filter_active().all())
        elif project_type == ProjectType.SUSPENDED.name:
            projects_list = list(Project.objects.filter_suspended().all())
        elif project_type == ProjectType.COMPLETED.name:
            projects_list = list(Project.objects.filter_completed().all())
        else:
            raise UnsupportedProjectTypeException("Unsupported project type")

        return projects_list

    def add_specified_users_to_project(
        self, project: Any, users_to_add_to_project: List[Any], as_manager: bool
    ) -> None:
        for user in users_to_add_to_project:
            if as_manager:
                self._add_manager_to_project_if_not_added_yet(project, user)
                self._add_member_to_project_if_not_added_yet(project, user)
            else:
                self._add_member_to_project_if_not_added_yet(project, user)

    @staticmethod
    def _add_manager_to_project_if_not_added_yet(project: Any, manager: Any) -> None:
        if not project.managers.filter(pk=manager.pk).exists():
            project.managers.add(manager)

    @staticmethod
    def _add_member_to_project_if_not_added_yet(project: Any, member: Any) -> None:
        if not project.members.filter(pk=member.pk).exists():
            project.members.add(member)

    def remove_all_random_user_projects(self, user_type: str) -> None:
        random_user = random.choice(self._get_list_of_users(user_type))

        if user_type == CustomUser.UserType.MANAGER.name:
            random_user.manager_projects.clear()
            random_user.projects.clear()
        else:
            random_user.projects.clear()

    def add_arguments(self, parser: Any) -> None:
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
        parser.add_argument(
            "--data-size",
            dest=DATA_SIZE_PARAMETER,
            metavar="size",
            choices=[DataSize.SMALL.value, DataSize.MEDIUM.value, DataSize.LARGE.value, DataSize.EXTRA_LARGE.value],
            help="Use prepared data set of given size to generate test data",
        )
