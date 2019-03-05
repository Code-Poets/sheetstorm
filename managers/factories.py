import factory
import factory.fuzzy

from managers.models import Project


class ProjectFactory(factory.DjangoModelFactory):

    class Meta:
        model = Project

    name = factory.Faker('sentence', nb_words=3)
    start_date = factory.Faker('date')
