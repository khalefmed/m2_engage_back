from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Avg, Count
from django.db.models.functions import TruncDate
from .models import Order
from .serializers import OrderSerializer
from marketing.permissions import IsAgent

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.all().select_related('client').prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAgent]

    # --- ACTION 1 : Statistiques Globales (KPIs) ---
    # Accessible via GET /api/sales/stats/
    @action(detail=False, methods=['get'])
    def stats(self, request):
        stats_data = Order.objects.aggregate(
            total_revenue=Sum('total_amount'),
            average_order_value=Avg('total_amount'),
            total_orders_count=Count('id')
        )
        
        # On peut ajouter un calcul de croissance ici (statique pour l'exemple)
        stats_data['growth_percentage'] = "+12.5%" 
        
        return Response(stats_data)

    # --- ACTION 2 : Données de Graphique (Série temporelle) ---
    # Accessible via GET /api/sales/chart_data/
    @action(detail=False, methods=['get'], url_path='chart-data')
    def chart_data(self, request):
        # On groupe par date et on somme les ventes
        data = (
            Order.objects
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(sales=Sum('total_amount'), orders=Count('id'))
            .order_by('date')
        )
        return Response(data)