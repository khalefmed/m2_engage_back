from django.db import models
from django.conf import settings
from clients.models import Customer
from django.db.models import Q
from datetime import date, timedelta

class Segment(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    rules = models.JSONField(help_text="Filtres dynamiques au format JSON")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_queryset(self):
        """
        Convertit le JSON en un QuerySet Django filtré.
        Exemple rule: {"gender": "M", "city": "Nouakchott"}
        """
        qs = Customer.objects.all()
        filters = Q()

        # 1. Filtres basiques (Egalité)
        if 'gender' in self.rules:
            filters &= Q(gender=self.rules['gender'])
        if 'country' in self.rules:
            filters &= Q(country=self.rules['country'])
        if 'city' in self.rules:
            filters &= Q(city=self.rules['city'])

        # 2. Filtres d'âge (Calculé à partir de date_of_birth)
        today = date.today()
        if 'min_age' in self.rules:
            birth_date_limit = today.replace(year=today.year - self.rules['min_age'])
            filters &= Q(date_of_birth__lte=birth_date_limit)
        if 'max_age' in self.rules:
            birth_date_limit = today.replace(year=today.year - self.rules['max_age'])
            filters &= Q(date_of_birth__gte=birth_date_limit)

        # 3. Filtre d'inactivité (Basé sur les dernières commandes)
        if 'inactive_days_gt' in self.rules:
            last_date = today - timedelta(days=self.rules['inactive_days_gt'])
            # Exclure les clients qui ont commandé après cette date
            qs = qs.exclude(orders__created_at__gte=last_date)

        return qs.filter(filters).distinct()

    @property
    def customer_count(self):
        return self.get_queryset().count()

    def __str__(self):
        return f"{self.name} ({self.customer_count} clients)"