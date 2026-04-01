from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer # À créer
from marketing.permissions import IsAdmin
from rest_framework import filters

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    permission_classes = [IsAdmin]