from rest_framework.views import APIView
from rest_framework.response import Response
from .services import AnalyticsService
from marketing.permissions import IsAdmin

class GlobalDashboardView(APIView):
    permission_classes = [IsAdmin] # Seuls les admins voient les stats globales

    def get(self, request):
        data = AnalyticsService.get_client_distribution()
        return Response(data)

class MapDataView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        points = AnalyticsService.get_geo_data()
        return Response(points)


class KPIStatsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        kpis = AnalyticsService.get_kpis()
        return Response(kpis)