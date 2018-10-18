from django.urls import include, path
from rest_framework import routers
from managers import views


router = routers.DefaultRouter()
router.register(r'projects', views.ProjectViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
