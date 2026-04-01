from django.urls import path
from .views import GlobalDashboardView, KPIStatsView, MapDataView

urlpatterns = [
    path('dashboard/', GlobalDashboardView.as_view(), name='analytics-dashboard'),
    path('map-points/', MapDataView.as_view(), name='analytics-map'),
    path('kpis/', KPIStatsView.as_view(), name='kpi-stats'),
]