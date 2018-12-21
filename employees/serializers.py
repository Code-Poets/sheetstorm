from rest_framework import serializers

from employees.common.constants import ReportModelConstants
from employees.models import Report
from managers.models import Project


class ReportSerializer(serializers.HyperlinkedModelSerializer):

    project = serializers.SlugRelatedField(
        queryset=Project.objects.all(),
        slug_field='name',
    )
    author = serializers.StringRelatedField()
    description = serializers.CharField(
        style={'base_template': 'textarea.html'},
        max_length=ReportModelConstants.MAX_DESCRIPTION_LENGTH.value
    )

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
