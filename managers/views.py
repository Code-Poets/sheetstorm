from django.db.models import Count
from django.db.models.functions import Lower
from django.views.generic import ListView
from rest_framework import renderers
from rest_framework import viewsets

from managers.models import Project
from managers.serializers import ProjectSerializer
from users.models import CustomUser


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by(Lower('name'))
    serializer_class = ProjectSerializer


class ProjectsList(ListView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'managers/projects_list.html'

    def get_queryset(self):
        if self.request.user.user_type == CustomUser.UserType.ADMIN.name:
            projects_queryset = Project.objects.all().order_by('id')
        elif self.request.user.user_type == CustomUser.UserType.MANAGER.name:
            projects_queryset = Project.objects.filter(managers__id=self.request.user.pk)
        else:
            projects_queryset = Project.objects.none()
        if self.request.GET.get('sort'):
            if 'members' in self.request.GET.get('sort'):
                projects_queryset = Project.objects.annotate(members_count=Count('members')) \
                    .order_by(self.request.GET.get('sort'))
            else:
                projects_queryset = projects_queryset.order_by(self.request.GET.get('sort'))

        return projects_queryset
