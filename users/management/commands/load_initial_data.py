from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from employees.factories import ReportFactory
from managers.factories import ProjectFactory
from managers.models import Project
from users.factories import UserFactory

User = get_user_model()


class Command(BaseCommand):
    help = "Create initial sample data for SheetStorm application testing."

    @transaction.atomic
    def handle(self, *args, **options):
        #
        # Users
        #

        user_admin = User.objects.filter(email="admin@codepoets.it").first()
        if user_admin is None:
            user_admin = UserFactory(
                email="admin@codepoets.it", user_type=User.UserType.ADMIN.name, is_superuser=True, is_staff=True
            )
            user_admin.set_password("superuser")  # pylint: disable=no-value-for-parameter
            user_admin.save()

        user_employee_1 = User.objects.filter(email="user1@codepoets.it").first()
        if user_employee_1 is None:
            user_employee_1 = UserFactory(
                email="user1@codepoets.it",
                user_type=User.UserType.EMPLOYEE.name,
                first_name="Mieczysław",
                last_name="Mietkowiak",
                phone_number="123456789012345",
                date_of_birth="1962-10-10",
            )
            user_employee_1.set_password("passwduser")  # pylint: disable=no-value-for-parameter
            user_employee_1.save()

        user_employee_2 = User.objects.filter(email="user2@codepoets.it").first()
        if user_employee_2 is None:
            user_employee_2 = UserFactory(
                email="user2@codepoets.it",
                user_type=User.UserType.EMPLOYEE.name,
                first_name="Andromeda",
                last_name="Adamiak",
            )
            user_employee_2.set_password("passwduser")  # pylint: disable=no-value-for-parameter
            user_employee_2.save()

        user_manager_1 = User.objects.filter(email="user3@codepoets.it").first()
        if user_manager_1 is None:
            user_manager_1 = UserFactory(
                email="user3@codepoets.it",
                user_type=User.UserType.MANAGER.name,
                first_name="Jan",
                last_name="Nowakowski",
            )
            user_manager_1.set_password("passwduser")  # pylint: disable=no-value-for-parameter
            user_manager_1.save()

        user_manager_2 = User.objects.filter(email="user4@codepoets.it").first()
        if user_manager_2 is None:
            user_manager_2 = UserFactory(
                email="user4@codepoets.it",
                user_type=User.UserType.MANAGER.name,
                first_name="Anna",
                last_name="Małomówna",
            )
            user_manager_2.set_password("passwduser")  # pylint: disable=no-value-for-parameter
            user_manager_2.save()

        user_employee_3 = User.objects.filter(email="user5@codepoets.it").first()
        if user_employee_3 is None:
            user_employee_3 = UserFactory(
                email="user5@codepoets.it",
                user_type=User.UserType.EMPLOYEE.name,
                first_name="Kurt",
                last_name="Schmidt",
                country="DE",
            )
            user_employee_3.set_password("passwduser")  # pylint: disable=no-value-for-parameter
            user_employee_3.save()

        #
        # Projects
        #

        project_stopped = Project.objects.filter(name="Time monkey").first()
        if project_stopped is None:
            project_stopped = ProjectFactory(
                name="Time monkey",
                start_date=timezone.now() - timezone.timedelta(days=4 * 7),
                stop_date=timezone.now() - timezone.timedelta(days=2 * 7),
            )

        self._add_manager_to_project_if_not_added_yet(project_stopped, user_manager_1)
        self._add_member_to_project_if_not_added_yet(project_stopped, user_employee_1)
        self._add_member_to_project_if_not_added_yet(project_stopped, user_employee_2)
        self._add_member_to_project_if_not_added_yet(project_stopped, user_manager_1)
        self._add_member_to_project_if_not_added_yet(project_stopped, user_manager_2)

        project_pending = Project.objects.filter(name="Sheet storm").first()
        if project_pending is None:
            project_pending = ProjectFactory(
                name="Sheet storm", start_date=timezone.now() - timezone.timedelta(days=2 * 7)
            )

        self._add_manager_to_project_if_not_added_yet(project_pending, user_manager_1)
        self._add_member_to_project_if_not_added_yet(project_pending, user_employee_1)
        self._add_member_to_project_if_not_added_yet(project_pending, user_employee_2)
        self._add_member_to_project_if_not_added_yet(project_pending, user_manager_1)

        project_terminated = Project.objects.filter(name="e_munchkin").first()
        if project_terminated is None:
            project_terminated = ProjectFactory(
                name="e_munchkin", start_date=timezone.now() - timezone.timedelta(days=7), terminated=True
            )

        self._add_manager_to_project_if_not_added_yet(project_terminated, user_manager_1)
        self._add_member_to_project_if_not_added_yet(project_terminated, user_employee_2)
        self._add_member_to_project_if_not_added_yet(project_terminated, user_employee_3)
        self._add_member_to_project_if_not_added_yet(project_terminated, user_manager_1)
        self._add_member_to_project_if_not_added_yet(project_terminated, user_manager_2)

        #
        # Reports
        #

        ReportFactory(
            date=timezone.now() - timezone.timedelta(days=2),
            description="Some report\r\ncontaining multiple lines\r\\nin description.",
            author=user_employee_1,
            project=project_pending,
            work_hours=timezone.timedelta(hours=8),
            editable=True,
        )

        ReportFactory(
            date=timezone.now() - timezone.timedelta(days=1),
            description="Some report",
            author=user_employee_1,
            project=project_pending,
            work_hours=timezone.timedelta(hours=4),
            editable=True,
        )

        ReportFactory(
            date=timezone.now() - timezone.timedelta(days=1),
            description="Some report on the same day as other.",
            author=user_employee_1,
            project=project_stopped,
            work_hours=timezone.timedelta(hours=4),
            editable=True,
        )

        ReportFactory(
            date=timezone.now() - timezone.timedelta(days=1),
            description="Some report",
            author=user_employee_2,
            project=project_pending,
            work_hours=timezone.timedelta(hours=6),
            editable=True,
        )

        ReportFactory(
            date=timezone.now() - timezone.timedelta(days=2),
            description="Some report containing hours with fraction",
            author=user_employee_2,
            project=project_terminated,
            work_hours=timezone.timedelta(hours=8, minutes=30),
            editable=True,
        )

        ReportFactory(
            date=timezone.now() - timezone.timedelta(days=2),
            description="Some report containing:\r\n- multiple lines\\ in description\r\n- time with fraction",
            author=user_manager_1,
            project=project_pending,
            work_hours=timezone.timedelta(hours=7, minutes=59),
            editable=True,
        )

        ReportFactory(
            date=timezone.now() - timezone.timedelta(days=1),
            description="Some report",
            author=user_manager_1,
            project=project_pending,
            work_hours=timezone.timedelta(hours=2),
            editable=True,
        )

        ReportFactory(
            date=timezone.now() - timezone.timedelta(days=1),
            description="Some report containing time with fraction.",
            author=user_manager_2,
            project=project_stopped,
            work_hours=timezone.timedelta(hours=7, minutes=1),
            editable=True,
        )

        ReportFactory(
            date=timezone.now() - timezone.timedelta(days=2),
            description="Some report",
            author=user_manager_2,
            project=project_terminated,
            work_hours=timezone.timedelta(hours=8),
            editable=True,
        )

        ReportFactory(
            date=timezone.now() - timezone.timedelta(days=1),
            description="Some report on the same day as other",
            author=user_manager_1,
            project=project_stopped,
            work_hours=timezone.timedelta(hours=2),
            editable=True,
        )

        ReportFactory(
            date=timezone.now() - timezone.timedelta(days=1),
            description="Some report on the same day as other two",
            author=user_manager_1,
            project=project_terminated,
            work_hours=timezone.timedelta(hours=4),
            editable=True,
        )

        ReportFactory(
            date=timezone.now() - timezone.timedelta(days=1),
            description="Some report",
            author=user_employee_3,
            project=project_terminated,
            work_hours=timezone.timedelta(hours=8),
            editable=True,
        )

    @staticmethod
    def _add_member_to_project_if_not_added_yet(project, member):
        if not project.members.filter(pk=member.pk).exists():
            project.members.add(member)

    @staticmethod
    def _add_manager_to_project_if_not_added_yet(project, manager):
        if not project.managers.filter(pk=manager.pk).exists():
            project.managers.add(manager)
