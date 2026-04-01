from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Choix des rôles
    ROLE_CHOICES = (
        ('superadmin', 'Super Administrateur'),
        ('admin', 'Administrateur'),
        ('agent', 'Agent Marketing'),
    )
    
    email = models.EmailField(unique=True) # On rend l'email unique
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='agent')
    
    mfa_secret = models.CharField(max_length=32, blank=True, null=True)
    is_mfa_enabled = models.BooleanField(default=False)

    # USERNAME_FIELD = 'email' 
    # REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.username} ({self.role})"