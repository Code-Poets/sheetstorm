from rest_framework import serializers

from employees.models import Report
from managers.models import Project


class ReportSerializer(serializers.HyperlinkedModelSerializer):

    project = serializers.SlugRelatedField(
        queryset=Project.objects.all(),
        slug_field='name',
    )
    author = serializers.StringRelatedField()

    class Meta:
        model = Report
        fields = (
            'url',
            'date',
            'project',
            'author',
            'description',
            'work_hours',
        )
