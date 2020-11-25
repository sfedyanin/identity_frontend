from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'id_servers'

router = DefaultRouter()
router.register(r'servers',
     views.ViServerViewSet, basename='server'),
router.register(r'server_groups',
     views.ViServerGroupViewSet, basename='servergroup'),
urlpatterns = router.urls