from django.conf.urls import url

from managers import views

urlpatterns = [
    url("^projects/$", views.ProjectsListView.as_view(), name="custom-projects-list"),
    url("^projects/create/$", views.ProjectCreateView.as_view(), name="custom-project-create"),
    url("^projects/(?P<pk>[0-9]+)/$", views.ProjectDetailView.as_view(), name="custom-project-detail"),
    url("^projects/(?P<pk>[0-9]+)/update/$", views.ProjectUpdateView.as_view(), name="custom-project-update"),
    url("^projects/(?P<pk>[0-9]+)/delete/$", views.ProjectDeleteView.as_view(), name="custom-project-delete"),
    url(
        "^project/(?P<pk>[0-9]+)/task-activities/$",
        views.ManageTaskActivitiesInProjectView.as_view(),
        name="project-task-activities",
    ),
    url(
        "^project/(?P<pk>[0-9]+)/remove-task-activity/(?P<task_activity_pk>[0-9]+)$",
        views.RemoveTaskActivityFromProjectView.as_view(),
        name="remove-task-activity-from-project",
    ),
]
