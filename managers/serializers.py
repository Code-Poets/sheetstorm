from rest_framework import serializers
from managers.models import Project


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = (
            'url',
            'name',
            'start_date',
            'stop_date',
            'terminated',
            #  'managers',
            #  'members',
        )
