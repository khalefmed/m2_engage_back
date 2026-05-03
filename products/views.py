from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from django.db.models import Sum, Q, DecimalField, IntegerField
from django.db.models.functions import Coalesce
from .models import Product
from .serializers import ProductSerializer
from marketing.permissions import IsAdmin

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    
    # Autorise le tri sur les noms d'annotations
    ordering_fields = ['total_sales', 'total_revenue', 'name', 'created_at']
    ordering = ['-total_revenue']

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        period_filter = Q()
        if start_date:
            period_filter &= Q(order_items__order__created_at__gte=start_date)
        if end_date:
            period_filter &= Q(order_items__order__created_at__lte=end_date)

        return Product.objects.annotate(
            total_sales=Coalesce(
                Sum('order_items__quantity', filter=period_filter), 
                0,
                output_field=IntegerField()
            ),
            total_revenue=Coalesce(
                Sum('order_items__subtotal', filter=period_filter), 
                0, # On met 0 en entier, l'output_field fera la conversion
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        ).all()