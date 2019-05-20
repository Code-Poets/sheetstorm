from enum import Enum

from django.utils.translation import ugettext_lazy as _

from utils.mixins import NotCallableMixin

MAX_DECIMAL_VALUE_VALIDATOR_MESSAGE = _("Minutes cannot be greater than 59.")
MAX_HOURS_VALUE_VALIDATOR_MESSAGE = _("This value cannot be greater than 24:00.")
MIN_HOURS_VALUE_VALIDATOR_MESSAGE = _("This value must be greater than 0.")


class ReportListStrings(NotCallableMixin, Enum):
    PAGE_TITLE = _("Reports")
    CREATE_REPORT_BUTTON = _("Create")
    JOIN_PROJECT_BUTTON = _("Join project")
    JOIN_POPUP_HEADER = _("Join project")
    JOIN_POPUP_YES = _("Join")
    JOIN_POPUP_NO = _("Cancel")
    DATE_COLUMN_HEADER = _("Date")
    PROJECT_COLUMN_HEADER = _("Project")
    WORK_HOURS_COLUMN_HEADER = _("Work hours")
    TASK_ACTIVITIES_COLUMN_HEADER = _("Task Activity")
    DESCRIPTION_COLUMN_HEADER = _("Description")
    HOURS_PER_DAY_LABEL = _("Total hours")
    EDIT_REPORT_BUTTON = _("Edit")
    NO_PROJECTS_TO_JOIN = _("There are no other projects available.")


class ReportDetailStrings(NotCallableMixin, Enum):
    PAGE_TITLE = _("Report - ")
    UPDATE_REPORT_BUTTON = _("Update")
    DISCARD_CHANGES_BUTTON = _("Discard")
    DELETE_REPORT_BUTTON = _("Delete")
    DELETE_POPUP_MESSAGE = _("Are you sure you want to delete this report?")
    DELETE_POPUP_TITLE = _("Delete report")
    DELETE_POPUP_YES = _("Yes")
    DELETE_POPUP_NO = _("No")


class TaskActivitiesStrings(Enum):
    PROJECT_MANAGEMENT = _("Project Management")
    MEETING = _("Meeting")
    SPEC_AND_DOCS = _("Spec & Docs")
    DESING_AND_RESEARCH = _("Design & Research")
    FRONTED_DEVELOPMENT = _("Frontend Development")
    BACKEND_DEVELOPMENT = _("Backend Development")
    QUALITY_ASSURANCE_TESTING = _("Quality Assurance / Testing")
    TRAVEL = _("Travel")
    DEVOPS = _("DevOps")
    REVIEW = _("Review")
    CONFERENCE = _("Conference")
    OTHER = _("Other")
    ADMINISTRATIVE = _("Administrative")
    MARKETING = _("Marketing")
    TRAINING = _("Training")
    MENTORSHIP = _("Mentorship")
    GRAPHIC_DESIGN = _("Graphic design")


class AuthorReportListStrings(NotCallableMixin, Enum):
    PAGE_TITLE = _(": Reports")
    DATE_COLUMN_HEADER = _("Date")
    PROJECT_COLUMN_HEADER = _("Project")
    WORK_HOURS_COLUMN_HEADER = _("Work hours")
    DESCRIPTION_COLUMN_HEADER = _("Description")
    CREATION_DATE_COLUMN_HEADER = _("Created")
    LAST_UPDATE_COLUMN_HEADER = _("Last update")
    EDITED_COLUMN_HEADER = _("Edited")
    TASK_ACTIVITY_HEADER = _("Task Activity")
    HOURS_PER_DAY_LABEL = _("Total hours")
    NO_REPORTS_MESSAGE = _("This employee has no reports to display.")
    RETURN_BUTTON_MESSAGE = _("Back to employee list")


class AdminReportDetailStrings(NotCallableMixin, Enum):
    PAGE_TITLE = _("Report - ")
    UPDATE_REPORT_BUTTON = _("Update")
    DISCARD_CHANGES_BUTTON = _("Discard")


class ProjectReportListStrings(NotCallableMixin, Enum):
    PAGE_TITLE = _(": Reports")
    DATE_COLUMN_HEADER = _("Date")
    PROJECT_COLUMN_HEADER = _("Project")
    AUTHOR_COLUMN_HEADER = _("Author")
    WORK_HOURS_COLUMN_HEADER = _("Work hours")
    DESCRIPTION_COLUMN_HEADER = _("Description")
    CREATION_DATE_COLUMN_HEADER = _("Created")
    LAST_UPDATE_COLUMN_HEADER = _("Last update")
    EDITED_COLUMN_HEADER = _("Edited")
    TASK_ACTIVITY_HEADER = _("Task Activity")
    NO_REPORTS_MESSAGE = _("There are no reports for this project to display.")


class ProjectReportDetailStrings(NotCallableMixin, Enum):
    PAGE_TITLE = _("Report - ")
    UPDATE_REPORT_BUTTON = _("Update")
    DISCARD_CHANGES_BUTTON = _("Discard")


class ReportValidationStrings(NotCallableMixin, Enum):
    WORK_HOURS_SUM_FOR_GIVEN_DATE_FOR_SINGLE_AUTHOR_EXCEEDED = _(
        "Sum of work hours of all reports from a given day for single author must not exceed 24."
    )
