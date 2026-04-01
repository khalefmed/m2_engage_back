from django.db import models
from django.conf import settings
from segments.models import Segment
from clients.models import Customer

class Campaign(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Brouillon'),
        ('active', 'Active / En cours'),
        ('completed', 'Terminée'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    subject = models.CharField(max_length=255) # Sujet de l'email
    content = models.TextField() # Contenu HTML/Texte
    
    segments = models.ManyToManyField(Segment, related_name='campaigns')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class EmailLog(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Envoyé'),
        ('failed', 'Échec'),
        ('opened', 'Ouvert'),
        ('clicked', 'Cliqué'),
    )

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='logs')
    client = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    sent_at = models.DateTimeField(auto_now_add=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    message_id = models.CharField(max_length=255, null=True, blank=True) # ID unique SMTP