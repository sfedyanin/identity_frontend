from . import views
from rest_framework.routers import DefaultRouter

app_name = 'id_platforms'

router = DefaultRouter()
router.register(
     r'platforms',
     views.PlatformViewSet, basename='platform')
urlpatterns = router.urls