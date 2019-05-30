from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter

from employees import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"reports", views.ReportViewSet, "report")

# The API URLs are now determined automatically by the router.
urlpatterns = [
    url(r"^api/", include(router.urls)),
    url(r"^reports/$", views.ReportList.as_view(), name="custom-report-list"),
    url(r"^reports/(?P<pk>[0-9]+)/$", views.ReportDetail.as_view(), name="custom-report-detail"),
    url(r"^reports/(?P<pk>[0-9]+)/delete/$", views.delete_report, name="custom-report-delete"),
    url(r"^reports/author/(?P<pk>[0-9]+)/$", views.AuthorReportView.as_view(), name="author-report-list"),
    url(r"^reports/management/(?P<pk>[0-9]+)/$", views.AdminReportView.as_view(), name="admin-report-detail"),
    url(r"^reports/project/(?P<pk>[0-9]+)/$", views.ProjectReportList.as_view(), name="project-report-list"),
    url(r"^reports/project/report/(?P<pk>[0-9]+)/$", views.ProjectReportDetail.as_view(), name="project-report-detail"),
    url(r"^export/user-reports/(?P<pk>[0-9]+)/$", views.ExportUserReportView.as_view(), name="export-data-xlsx"),
    url(
        r"^export/project-reports/(?P<pk>[0-9]+)/$",
        views.ExportReportsInProjectView.as_view(),
        name="export-project-data-xlsx",
    ),
]
