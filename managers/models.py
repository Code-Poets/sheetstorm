from django.db import models
from managers.commons.constants import MAX_NAME_LENGTH
from users.models import CustomUser


class Project(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    start_date = models.DateField()
    stop_date = models.DateField(null=True, blank=True)
    terminated = models.BooleanField(default=False)
    managers = models.ManyToManyField(CustomUser, related_name="managers")
    members = models.ManyToManyField(CustomUser, related_name="members")

    def __str__(self):
        return self.name
