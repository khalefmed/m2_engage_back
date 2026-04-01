from rest_framework.routers import DefaultRouter
from .views import SegmentViewSet

router = DefaultRouter()
router.register(r'', SegmentViewSet)
urlpatterns = router.urls