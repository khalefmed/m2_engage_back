from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    # Les valeurs sont récupérées directement depuis les annotations du queryset
    total_sales = serializers.IntegerField(read_only=True)
    total_revenue = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        read_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 
            'name', 
            'description', 
            'category', 
            'price', 
            'is_active', 
            'total_sales', 
            'total_revenue', 
            'created_at'
        ]