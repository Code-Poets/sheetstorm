from django.db import models
from django.db.models import Q
from managers.commons.constants import MAX_NAME_LENGTH
from users.models import CustomUser


class ProjectQuerySet(models.QuerySet):
    def filter_terminated(self):
        return self.filter(terminated=True, stop_date=None)

    def filter_active(self):
        return self.filter(terminated=False, stop_date=None)

    def filter_completed(self):
        return self.filter(~Q(stop_date=None))


class Project(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    start_date = models.DateField()
    stop_date = models.DateField(null=True, blank=True)
    terminated = models.BooleanField(default=False)
    managers = models.ManyToManyField(CustomUser, related_name="managers")
    members = models.ManyToManyField(CustomUser, related_name="members")

    objects = ProjectQuerySet.as_manager()

    def __str__(self):
        return self.name
