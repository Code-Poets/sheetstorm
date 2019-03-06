import datetime

from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from django.test import TestCase

from users.models import CustomUser
from managers import views
from managers.models import Project


class DeleteProjectTests(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it",
            first_name='John',
            last_name='Doe',
            country='PL',
            user_type=CustomUser.UserType.ADMIN.name,
        )
        self.user.password = 'newuserpasswd'
        self.user.set_password(self.user.password)
        self.user.full_clean()
        self.user.save()

        self.project = Project(
            name='Example Project',
            start_date=datetime.datetime.now().date() - datetime.timedelta(days=30),
            stop_date=datetime.datetime.now().date(),
            terminated=False,
        )
        self.project.full_clean()
        self.project.save()
        self.project.managers.add(self.user)
        self.project.members.add(self.user)
        self.url = reverse('custom-project-delete', args=(self.project.pk,))

    def test_delete_project_function_view_should_delete_project_on_admin_type_user_post(self):
        project_object_count_befor_post = Project.objects.all().count()
        request = APIRequestFactory().post(
            path=self.url,
        )
        request.user = self.user
        response = views.delete_project(request, self.project.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.all().count(), project_object_count_befor_post - 1)
        with self.assertRaises(Project.DoesNotExist) as exception:
            Project.objects.get(name=self.project.name)
        self.assertTrue("Project matching query does not exist" in str(exception.exception))

    def test_delete_project_function_view_should_not_delete_project_on_employee_type_user_post(self):
        self.user.user_type = CustomUser.UserType.EMPLOYEE.name
        project_object_count_befor_post = Project.objects.all().count()
        request = APIRequestFactory().post(
            path=self.url,
        )
        request.user = self.user
        response = views.delete_project(request, self.project.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.all().count(), project_object_count_befor_post)
        self.assertTrue(Project.objects.get(name=self.project.name))

    def test_delete_project_function_view_should_not_delete_project_on_manager_type_user_post(self):
        self.user.user_type = CustomUser.UserType.MANAGER.name
        project_object_count_befor_post = Project.objects.all().count()
        request = APIRequestFactory().post(
            path=self.url,
        )
        request.user = self.user
        response = views.delete_project(request, self.project.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.all().count(), project_object_count_befor_post)
        self.assertTrue(Project.objects.get(name=self.project.name))
