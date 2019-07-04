from enum import Enum

from django.utils.translation import ugettext_lazy as _

from common.constants import CORRECT_DATE_FORMAT


class ProjectConstants(Enum):
    MAX_NAME_LENGTH = 64
    MESSAGE_FOR_CORRECT_DATE_FORMAT = f"Please enter date in this format: {CORRECT_DATE_FORMAT}"
    STOP_DATE_VALIDATION_ERROR_MESSAGE = _("A project can not be created after expired date!")
