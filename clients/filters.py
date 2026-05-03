import django_filters
from django.utils import timezone
from .models import Customer

class CustomerFilter(django_filters.FilterSet):
    # On définit des méthodes personnalisées pour calculer les dates
    min_age = django_filters.NumberFilter(method='filter_min_age')
    max_age = django_filters.NumberFilter(method='filter_max_age')
    gender = django_filters.CharFilter(field_name='gender', lookup_expr='exact')

    class Meta:
        model = Customer
        fields = ['country', 'city', 'gender']

    def filter_min_age(self, queryset, name, value):
        # Si je veux des gens d'AU MOINS 40 ans, 
        # ils doivent être nés AVANT (ou en) 1986
        current_year = timezone.now().year
        target_year = current_year - int(value)
        return queryset.filter(date_of_birth__year__lte=target_year)

    def filter_max_age(self, queryset, name, value):
        # Si je veux des gens de MAXIMUM 25 ans, 
        # ils doivent être nés APRÈS (ou en) 2001
        current_year = timezone.now().year
        target_year = current_year - int(value)
        return queryset.filter(date_of_birth__year__gte=target_year)