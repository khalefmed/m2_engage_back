from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Campaign, EmailLog
from .serializers import CampaignSerializer
from .tasks import send_campaign_emails_task
from marketing.permissions import IsAgent
from rest_framework.decorators import action

# 1. Vue pour le CRUD des campagnes
class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all().prefetch_related('segments', 'logs')
    serializer_class = CampaignSerializer
    permission_classes = [IsAgent]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Déclenchement de Celery si la campagne passe de draft à active
        if request.data.get('status') == 'active' and instance.status == 'draft':
            send_campaign_emails_task.delay(instance.id)
            
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='send')
    def send_campaign(self, request, pk=None):
        campaign = self.get_object()
        
        if campaign.status != 'draft':
            return Response({"error": "Seules les campagnes en brouillon peuvent être envoyées."}, status=400)

        campaign.status = 'queued'
        campaign.save()

        return Response({
            "message": "L'envoi de la campagne a été mis en file d'attente.",
            "status": "queued"
        })

# 2. Vue pour le tracking (le pixel invisible)
class EmailOpenTrackingView(APIView):
    permission_classes = []  # Public pour être chargé par les clients mail

    def get(self, request, log_id):
        log = get_object_or_404(EmailLog, id=log_id)
        
        if log.status != 'opened':
            log.status = 'opened'
            log.opened_at = timezone.now()
            log.save()

        # Image PNG 1x1 transparente
        PIXEL_1X1 = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01'
            b'\x00\x00\x02\x00\x01\xe6\xd1C\xed\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        return HttpResponse(PIXEL_1X1, content_type="image/png")