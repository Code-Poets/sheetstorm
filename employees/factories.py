import factory
import factory.fuzzy

from employees.models import Report


class ReportFactory(factory.DjangoModelFactory):
    class Meta:
        model = Report

    date = factory.Faker("date")
    author = factory.SubFactory("users.factories.UserFactory")
    project = factory.SubFactory("managers.factories.ProjectFactory")
    work_hours = factory.fuzzy.FuzzyInteger(1, 8, 1)
