from rest_framework import serializers

from employees.common.constants import ReportModelConstants
from employees.common.validators import MaxDecimalValueValidator
from employees.models import Report
from managers.models import Project


class HoursField(serializers.DecimalField):
    def __init__(self, **kwargs):
        super().__init__(
            max_value=ReportModelConstants.MAX_WORK_HOURS.value,
            min_value=ReportModelConstants.MIN_WORK_HOURS.value,
            max_digits=ReportModelConstants.MAX_DIGITS.value,
            decimal_places=ReportModelConstants.DECIMAL_PLACES.value,
            validators=[MaxDecimalValueValidator(ReportModelConstants.MAX_WORK_HOURS_DECIMAL_VALUE.value)],
            **kwargs)

    def to_internal_value(self, data):
        if isinstance(data, str) and ':' in data:
            converted = data.replace(':', '.')
            return super().to_internal_value(converted)
        return super().to_internal_value(data)


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

    work_hours = HoursField()

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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(self.instance, Report):
            data['work_hours'] = self.instance.work_hours_str
        return data
