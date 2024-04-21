from .views import WorkProfileViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', WorkProfileViewSet, basename='work_profile')
urlpatterns = router.urls

