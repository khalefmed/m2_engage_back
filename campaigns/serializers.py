from rest_framework import serializers
from .models import Campaign

class CampaignSerializer(serializers.ModelSerializer):
    sent_count = serializers.IntegerField(source='logs.count', read_only=True)
    open_count = serializers.SerializerMethodField()
    
    # Correction : On marque created_by en lecture seule pour qu'il soit rempli par le backend
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'description', 'subject', 'content', 
            'segments', 'status', 'start_date', 'created_by', 
            'sent_count', 'open_count', 'created_at'
        ]
        # Optionnel : Rendre certains champs non-obligatoires pour le POST
        extra_kwargs = {
            'description': {'required': False, 'allow_blank': True},
            'start_date': {'required': False, 'allow_null': True},
            'status': {'read_only': True} # Le statut est géré par le backend (draft par défaut)
        }

    def get_open_count(self, obj):
        # Utilisation de .exists() ou d'une vérification de relation pour éviter les erreurs si logs n'existe pas
        if hasattr(obj, 'logs'):
            return obj.logs.filter(status='opened').count()
        return 0