from django.contrib import admin

from employees.models import Report
from employees.models import TaskActivityType

admin.site.register(Report)


class TaskActivities(admin.ModelAdmin):
    list_display = ("name",)


admin.site.register(TaskActivityType, TaskActivities)
