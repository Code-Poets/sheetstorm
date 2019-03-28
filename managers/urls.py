from django.conf.urls import url
from django.urls import include
from rest_framework import routers
from managers import views


router = routers.DefaultRouter()
router.register(r'projects', views.ProjectViewSet, 'project')

urlpatterns = [
    url('^api/', include(router.urls)),
    url('^projects/$', views.ProjectsList.as_view(), name='custom-projects-list'),
    url('^projects/(?P<pk>[0-9]+)/$', views.ProjectDetail.as_view(), name='custom-project-detail'),
]
