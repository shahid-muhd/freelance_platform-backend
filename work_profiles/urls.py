from .views import WorkProfileViewSet,PortfolioViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'profile', WorkProfileViewSet, basename='work_profile')
router.register(r'portfolio', PortfolioViewSet, basename='portfolio_viewset')
urlpatterns = router.urls

