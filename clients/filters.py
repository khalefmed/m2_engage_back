import django_filters
from .models import Customer

class CustomerFilter(django_filters.FilterSet):
    min_age = django_filters.NumberFilter(field_name="date_of_birth", lookup_expr='year__lt') # Simplifié
    max_age = django_filters.NumberFilter(field_name="date_of_birth", lookup_expr='year__gt')
    
    class Meta:
        model = Customer
        fields = {
            'country': ['exact', 'icontains'],
            'city': ['exact', 'icontains'],
            'gender': ['exact'],
            'profession': ['icontains'],
        }