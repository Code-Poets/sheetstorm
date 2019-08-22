import factory
import factory.fuzzy

from users.models import CustomUser


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.LazyAttributeSequence(
        lambda o, n: "{0}.{1}+profile{2}@codepoets.it".format(o.first_name, o.last_name, n).lower()
    )
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True

    @factory.post_generation
    def set_password(  # type: ignore
        self, create, extracted, **kwargs
    ):  # pylint: disable=unused-argument, no-value-for-parameter
        self.set_password("userpasswd")
        if create:
            self.save()


class AdminUserFactory(UserFactory):

    user_type = CustomUser.UserType.ADMIN.name


class ManagerUserFactory(UserFactory):

    user_type = CustomUser.UserType.MANAGER.name
