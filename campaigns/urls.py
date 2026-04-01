from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CampaignViewSet, EmailOpenTrackingView

router = DefaultRouter()
router.register(r'', CampaignViewSet)

urlpatterns = [
    path('track/open/<int:log_id>/', EmailOpenTrackingView.as_view(), name='email-track-open'),
    path('', include(router.urls)),
]