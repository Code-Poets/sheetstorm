import datetime

import factory
import factory.fuzzy

from employees.models import Report
from employees.models import TaskActivityType


class ReportFactory(factory.DjangoModelFactory):
    class Meta:
        model = Report

    date = factory.Faker("date")
    author = factory.SubFactory("users.factories.UserFactory")
    project = factory.SubFactory("managers.factories.ProjectFactory")
    work_hours = factory.LazyFunction(lambda: datetime.timedelta(hours=8))
    description = factory.fuzzy.FuzzyText()
    task_activities = factory.SubFactory("employees.factories.TaskActivityTypeFactory")


class TaskActivityTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = TaskActivityType

    name = factory.fuzzy.FuzzyText()
