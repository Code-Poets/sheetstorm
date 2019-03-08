from django.test import TestCase
from managers.serializers import ProjectSerializer
from users.models import CustomUser


class TestProjectSerializer(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email='testuser@codepoets.it',
            password='newuserpasswd',
            first_name='John',
            last_name='Doe',
            country='PL'
        )
        self.user.full_clean()
        self.user.save()

    def test_serializer_should_accept_valid_input(self):
        valid_input = {
            'name': 'Example Project',
            'start_date': '2018-11-11',
            'stop_date': '2018-11-12',
            'terminated': True,
            'managers': [self.user.pk, ],
            'members': [self.user.pk, ],
        }
        example_project = ProjectSerializer(data=valid_input)
        self.assertTrue(example_project.is_valid())
