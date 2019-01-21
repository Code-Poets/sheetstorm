import datetime
from django.test import TestCase

from employees.forms import ProjectJoinForm
from managers.models import Project


class ProjectJoinFormTests(TestCase):
    def test_project_join_form_should_create_choice_field_with_project_name_and_id_based_on_queryset_provided_in_constructor(self):
        queryset_length = 10
        for i in range(queryset_length):
            project = Project(
                name=f"Test Project {i}",
                start_date=datetime.datetime.now(),
            )
            project.full_clean()
            project.save()
        queryset = Project.objects.all()
        form = ProjectJoinForm(queryset)
        choices = form.fields['projects'].choices
        self.assertIsNotNone(choices)
        self.assertEqual(len(choices), queryset_length)
        for i in range(queryset_length):
            self.assertEqual(choices[i][0], queryset[i].id)
            self.assertEqual(choices[i][1], queryset[i].name)
