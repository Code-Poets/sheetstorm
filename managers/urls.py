from django.conf.urls import url
from django.urls import include
from rest_framework import routers
from managers import views


router = routers.DefaultRouter()
router.register(r'projects', views.ProjectViewSet, 'project')

urlpatterns = [
    url('^', include(router.urls)),
]
