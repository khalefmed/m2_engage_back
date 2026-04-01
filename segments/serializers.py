from rest_framework import serializers
from .models import Segment

class SegmentSerializer(serializers.ModelSerializer):
    customer_count = serializers.ReadOnlyField()
    created_by_name = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Segment
        fields = [
            'id', 'name', 'description', 'rules', 
            'customer_count', 'created_by', 'created_by_name', 
            'created_at', 'updated_at'
        ]
        
    def validate_rules(self, value):
        # Optionnel : Ajouter ici une validation pour vérifier que le JSON respecte 
        # le format attendu par ton moteur de segmentation
        if not isinstance(value, dict):
            raise serializers.ValidationError("Les règles doivent être un objet JSON (dictionnaire).")
        return value