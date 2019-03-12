from django.db.models.functions import Lower
from rest_framework import viewsets
from managers.models import Project
from managers.serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by(Lower('name'))
    serializer_class = ProjectSerializer
