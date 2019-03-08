from rest_framework import serializers

from managers.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class ProjectCreateSerializer(ProjectSerializer):
    class Meta:
        model = Project
        fields = (
            'name',
            'start_date',
            'terminated',
            'managers',
            'members',
        )
