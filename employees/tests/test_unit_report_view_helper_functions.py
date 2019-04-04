import datetime
from decimal import Decimal

from django.test import TestCase

from employees.models import Report
from employees.views import query_as_dict
from managers.models import Project
from users.models import CustomUser


class TestListHelpers(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it", password="newuserpasswd", first_name="John", last_name="Doe", country="PL"
        )
        self.user.full_clean()
        self.user.save()

        self.project = Project(name="Test Project", start_date=datetime.datetime.now())
        self.project.full_clean()
        self.project.save()

        report = Report(
            date=datetime.datetime.now().date(),
            description="Some description",
            author=self.user,
            project=self.project,
            work_hours=Decimal("8.00"),
        )
        report.full_clean()
        report.save()

        report = Report(
            date=datetime.datetime.now().date(),
            description="Some description",
            author=self.user,
            project=self.project,
            work_hours=Decimal("8.00"),
        )
        report.full_clean()
        report.save()

        report = Report(
            date=datetime.date(2001, 1, 1),
            description="Some description",
            author=self.user,
            project=self.project,
            work_hours=Decimal("8.00"),
        )
        report.full_clean()
        report.save()

    def test_queryset_as_dict_should_return_dictionary_where_keys_are_dates_and_values_are_lists_of_reports(self):
        queryset = Report.objects.all()
        dictionary = query_as_dict(queryset)
        self.assertEqual(len(dictionary), 2)
        self.assertEqual(len(list(dictionary.values())[0]), 2)
        self.assertEqual(len(list(dictionary.values())[1]), 1)
        self.assertIsInstance(list(dictionary.keys())[0], datetime.date)
        self.assertIsInstance(list(dictionary.keys())[1], datetime.date)
        self.assertIsInstance(list(dictionary.values())[0][0], Report)
        self.assertIsInstance(list(dictionary.values())[0][1], Report)
        self.assertIsInstance(list(dictionary.values())[1][0], Report)
