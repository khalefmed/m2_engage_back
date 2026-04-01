from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Customer
from .serializers import CustomerSerializer
from .filters import CustomerFilter
from marketing.permissions import IsAgent # Import de vos permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAgent] # Agents, Admins et Superadmins
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CustomerFilter
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['created_at', 'last_name']

    def get_queryset(self):
        # Optimisation : On évite les requêtes N+1 pour les calculs
        return super().get_queryset().prefetch_related('orders')
    
    @action(detail=False, methods=['get'])
    def map_stats(self, request):
        stats = Customer.objects.values('city').annotate(total=Count('id'))
        # Retourne un dictionnaire: {"Nouakchott": 1200, "Nouadhibou": 800...}
        data = {item['city']: item['total'] for item in stats if item['city']}
        return Response(data)