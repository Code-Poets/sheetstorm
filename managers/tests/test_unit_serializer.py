from django.test import TestCase
from managers.serializers import ProjectSerializer


class TestProjectSerializer(TestCase):
    def test_serializer_should_accept_valid_input(self):
        valid_input = {
            'name': 'Example Project',
            'start_date': '2018-11-11',
            'stop_date': '2018-11-12',
            'terminated': True,
        }
        example_project = ProjectSerializer(data=valid_input)
        self.assertTrue(example_project.is_valid())
