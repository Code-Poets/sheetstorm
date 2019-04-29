from enum import Enum

from django.utils.translation import ugettext_lazy

from utils.mixins import NotCallableMixin

MAX_DECIMAL_VALUE_VALIDATOR_MESSAGE = ugettext_lazy("Minutes cannot be greater than 59.")
MAX_HOURS_VALUE_VALIDATOR_MESSAGE = ugettext_lazy("This value cannot be greater than 24:00.")
MIN_HOURS_VALUE_VALIDATOR_MESSAGE = ugettext_lazy("This value must be greater than 0.")


class ReportListStrings(NotCallableMixin, Enum):
    PAGE_TITLE = ugettext_lazy("Reports")
    CREATE_REPORT_BUTTON = ugettext_lazy("Create")
    JOIN_PROJECT_BUTTON = ugettext_lazy("Join project")
    JOIN_POPUP_HEADER = ugettext_lazy("Join project")
    JOIN_POPUP_YES = ugettext_lazy("Join")
    JOIN_POPUP_NO = ugettext_lazy("Cancel")
    DATE_COLUMN_HEADER = ugettext_lazy("Date")
    PROJECT_COLUMN_HEADER = ugettext_lazy("Project")
    WORK_HOURS_COLUMN_HEADER = ugettext_lazy("Work hours")
    TASK_ACTIVITIES_COLUMN_HEADER = ugettext_lazy("Task Activity")
    DESCRIPTION_COLUMN_HEADER = ugettext_lazy("Description")
    EDIT_REPORT_BUTTON = ugettext_lazy("Edit")


class ReportDetailStrings(NotCallableMixin, Enum):
    PAGE_TITLE = ugettext_lazy("Report - ")
    UPDATE_REPORT_BUTTON = ugettext_lazy("Update")
    DISCARD_CHANGES_BUTTON = ugettext_lazy("Discard")
    DELETE_REPORT_BUTTON = ugettext_lazy("Delete")
    DELETE_POPUP_MESSAGE = ugettext_lazy("Are you sure you want to delete this report?")
    DELETE_POPUP_TITLE = ugettext_lazy("Delete report")
    DELETE_POPUP_YES = ugettext_lazy("Yes")
    DELETE_POPUP_NO = ugettext_lazy("No")


class TaskActivitiesStrings(Enum):
    PROJECT_MANAGEMENT = ugettext_lazy("Project Management")
    MEETING = ugettext_lazy("Meeting")
    SPEC_AND_DOCS = ugettext_lazy("Spec & Docs")
    DESING_AND_RESEARCH = ugettext_lazy("Design & Research")
    FRONTED_DEVELOPMENT = ugettext_lazy("Frontend Development")
    BACKEND_DEVELOPMENT = ugettext_lazy("Backend Development")
    QUALITY_ASSURANCE_TESTING = ugettext_lazy("Quality Assurance / Testing")
    TRAVEL = ugettext_lazy("Travel")
    DEVOPS = ugettext_lazy("DevOps")
    REVIEW = ugettext_lazy("Review")
    CONFERENCE = ugettext_lazy("Conference")
    OTHER = ugettext_lazy("Other")
    ADMINISTRATIVE = ugettext_lazy("Administrative")
    MARKETING = ugettext_lazy("Marketing")
    TRAINING = ugettext_lazy("Training")
    MENTORSHIP = ugettext_lazy("Mentorship")
    GRAPHIC_DESIGN = ugettext_lazy("Graphic design")


class AuthorReportListStrings(NotCallableMixin, Enum):
    PAGE_TITLE = ugettext_lazy(": Reports")
    DATE_COLUMN_HEADER = ugettext_lazy("Date")
    PROJECT_COLUMN_HEADER = ugettext_lazy("Project")
    WORK_HOURS_COLUMN_HEADER = ugettext_lazy("Work hours")
    DESCRIPTION_COLUMN_HEADER = ugettext_lazy("Description")
    CREATION_DATE_COLUMN_HEADER = ugettext_lazy("Created")
    LAST_UPDATE_COLUMN_HEADER = ugettext_lazy("Last update")
    EDITED_COLUMN_HEADER = ugettext_lazy("Edited")
    TASK_ACTIVITY_HEADER = ugettext_lazy("Task Activity")
    NO_REPORTS_MESSAGE = ugettext_lazy("This employee has no reports to display.")
