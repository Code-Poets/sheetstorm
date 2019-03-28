from enum import Enum

from django.utils.translation import ugettext_lazy

from utils.decorators import notCallable


MAX_DECIMAL_VALUE_VALIDATOR_MESSAGE = ugettext_lazy('Ensure this value is less than or equal to ')


@notCallable
class ReportListStrings(Enum):
    PAGE_TITLE = ugettext_lazy("Reports")
    CREATE_REPORT_BUTTON = ugettext_lazy("Create")
    DATE_COLUMN_HEADER = ugettext_lazy("Date")
    PROJECT_COLUMN_HEADER = ugettext_lazy("Project")
    WORK_HOURS_COLUMN_HEADER = ugettext_lazy("Work hours")
    DESCRIPTION_COLUMN_HEADER = ugettext_lazy("Description")
    EDIT_REPORT_BUTTON = ugettext_lazy("Edit")


@notCallable
class ReportDetailStrings(Enum):
    PAGE_TITLE = ugettext_lazy("Report - ")
    UPDATE_REPORT_BUTTON = ugettext_lazy("Update")
    DISCARD_CHANGES_BUTTON = ugettext_lazy("Discard")
    DELETE_REPORT_BUTTON = ugettext_lazy("Delete")
    DELETE_POPUP_MESSAGE = ugettext_lazy("Are you sure you want to delete this report?")
    DELETE_POPUP_TITLE = ugettext_lazy("Delete report")
    DELETE_POPUP_YES = ugettext_lazy("Yes")
    DELETE_POPUP_NO = ugettext_lazy("No")
