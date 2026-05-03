from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

class Customer(models.Model):
    GENDER_CHOICES = (
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, db_index=True)
    date_of_birth = models.DateField(db_index=True)
    profession = models.CharField(max_length=150, blank=True, null=True)
    
    # Localisation
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, db_index=True)
    country = models.CharField(max_length=100, db_index=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            # Index composite pour les recherches fréquentes par zone géographique
            models.Index(fields=['country', 'city']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def is_active(self):
        # Un client est considéré actif s'il a passé une commande dans les 60 derniers jours
        last_order = self.orders.order_by('-created_at').first()
        if not last_order:
            return False
        return last_order.created_at > timezone.now() - timedelta(days=60)

    @property
    def last_purchase_date(self):
        last_order = self.orders.order_by('-created_at').first()
        return last_order.created_at if last_order else None

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))