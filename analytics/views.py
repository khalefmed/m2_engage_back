from rest_framework.views import APIView
from rest_framework.response import Response
from .services import AnalyticsService
from marketing.permissions import IsAdmin

class GlobalDashboardView(APIView):
    permission_classes = [IsAdmin] # Seuls les admins voient les stats globales

    def get(self, request):
        # On passe les paramètres de la requête (ex: ?segment=1&start_date=...) au service
        data = AnalyticsService.get_client_distribution(request.query_params)
        return Response(data)

class MapDataView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        # On passe les paramètres pour que la carte soit aussi filtrée par segment/date
        points = AnalyticsService.get_geo_data(request.query_params)
        return Response(points)


class KPIStatsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        # On passe les paramètres pour que les KPIs (CA, Panier moyen) s'adaptent au segment
        kpis = AnalyticsService.get_kpis(request.query_params)
        return Response(kpis)