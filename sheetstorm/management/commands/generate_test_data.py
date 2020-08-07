import logging

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from users.factories import UserFactory

CustomUser = get_user_model()

superuser_user_type = "SUPERUSER"


class Command(BaseCommand):
    help = "Create initial sample data for SheetStorm application testing."

    @transaction.atomic
    def handle(self, *args, **options):
        user_options = self._get_user_options(options)
        is_need_to_create_superuser = self._get_superuser_request(options)

        for (user_type, number_of_users) in user_options.items():
            if number_of_users is not None:
                self.create_user(user_type, number_of_users)

        if is_need_to_create_superuser:
            self.create_user(superuser_user_type)

        logging.info(f"Total number of users in the database: {CustomUser.objects.count()}")

    @staticmethod
    def _get_user_options(options):
        return {
            CustomUser.UserType.ADMIN.name: options[CustomUser.UserType.ADMIN.name],
            CustomUser.UserType.EMPLOYEE.name: options[CustomUser.UserType.EMPLOYEE.name],
            CustomUser.UserType.MANAGER.name: options[CustomUser.UserType.MANAGER.name],
        }

    @staticmethod
    def _get_superuser_request(options):
        is_superuser_create_request = options[superuser_user_type]
        is_superuser_in_database = CustomUser.objects.filter(is_superuser=True).exists()

        return is_superuser_create_request and not is_superuser_in_database

    def create_user(self, user_type, number_of_users_to_create=1):
        factory_parameters = self._set_user_factory_parameters(user_type)

        for user_number in range(number_of_users_to_create):
            user_email = f"user.{user_type}{user_number + 1}@codepoets.it".lower()

            if not CustomUser.objects.filter(email=user_email).exists():
                logging.info(f"{number_of_users_to_create - user_number} {user_type}(s) left to create")
                UserFactory(**factory_parameters, email=user_email)

    @staticmethod
    def _set_user_factory_parameters(user_type):
        return {
            "user_type": CustomUser.UserType.ADMIN.name if user_type == superuser_user_type else user_type,
            "is_staff": user_type in (CustomUser.UserType.ADMIN.name, superuser_user_type),
            "is_superuser": user_type == superuser_user_type,
        }

    def add_arguments(self, parser):
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
            dest=superuser_user_type,
            action="store_true",
            help="Create and add superuser to the database if not exist",
        )
