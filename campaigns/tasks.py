from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from .models import Campaign, EmailLog
from django.utils import timezone

@shared_task
def send_campaign_emails_task(campaign_id):
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        if campaign.status != 'active':
            return "Campagne non active"

        # On récupère tous les clients uniques de tous les segments de la campagne
        target_clients = set()
        for segment in campaign.segments.all():
            target_clients.update(segment.get_queryset())

        for client in target_clients:
            # Envoi réel (SMTP)
            # Note: Dans un vrai SaaS, on utiliserait un template HTML dynamique ici
            success = send_mail(
                subject=campaign.subject,
                message=campaign.content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client.email],
                fail_silently=True,
            )

            # Log de l'envoi
            EmailLog.objects.create(
                campaign=campaign,
                client=client,
                status='sent' if success else 'failed'
            )
        
        campaign.status = 'completed'
        campaign.save()
        return f"Campagne {campaign.name} terminée : {len(target_clients)} emails traités."
    
    except Campaign.DoesNotExist:
        return "Campagne introuvable"