from enum import Enum
from utils.decorators import do_not_call_in_templates

from django.utils.translation import ugettext_lazy

MAX_DECIMAL_VALUE_VALIDATOR_MESSAGE = ugettext_lazy("Minutes cannot be greater than 59.")
MAX_HOURS_VALUE_VALIDATOR_MESSAGE = ugettext_lazy("This value cannot be greater than 24:00.")
MIN_HOURS_VALUE_VALIDATOR_MESSAGE = ugettext_lazy("This value must be greater than 0.")


@do_not_call_in_templates
class ReportListStrings(Enum):
    PAGE_TITLE = ugettext_lazy("Reports")
    CREATE_REPORT_BUTTON = ugettext_lazy("Create")
    JOIN_PROJECT_BUTTON = ugettext_lazy("Join project")
    JOIN_POPUP_HEADER = ugettext_lazy("Join project")
    JOIN_POPUP_YES = ugettext_lazy("Join")
    JOIN_POPUP_NO = ugettext_lazy("Cancel")
    DATE_COLUMN_HEADER = ugettext_lazy("Date")
    PROJECT_COLUMN_HEADER = ugettext_lazy("Project")
    WORK_HOURS_COLUMN_HEADER = ugettext_lazy("Work hours")
    DESCRIPTION_COLUMN_HEADER = ugettext_lazy("Description")
    EDIT_REPORT_BUTTON = ugettext_lazy("Edit")


@do_not_call_in_templates
class ReportDetailStrings(Enum):
    PAGE_TITLE = ugettext_lazy("Report - ")
    UPDATE_REPORT_BUTTON = ugettext_lazy("Update")
    DISCARD_CHANGES_BUTTON = ugettext_lazy("Discard")
    DELETE_REPORT_BUTTON = ugettext_lazy("Delete")
    DELETE_POPUP_MESSAGE = ugettext_lazy("Are you sure you want to delete this report?")
    DELETE_POPUP_TITLE = ugettext_lazy("Delete report")
    DELETE_POPUP_YES = ugettext_lazy("Yes")
    DELETE_POPUP_NO = ugettext_lazy("No")
