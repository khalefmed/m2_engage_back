from rest_framework import serializers
from .models import Product
from django.db.models import Sum

class ProductSerializer(serializers.ModelSerializer):
    total_sales = serializers.SerializerMethodField()
    total_revenue = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 
            'price', 'is_active', 'total_sales', 
            'total_revenue', 'created_at'
        ]

    def get_total_sales(self, obj):
        # On calcule le nombre total d'unités vendues pour ce produit
        from sales.models import OrderItem
        return OrderItem.objects.filter(product=obj).aggregate(Sum('quantity'))['quantity__sum'] or 0

    def get_total_revenue(self, obj):
        # On calcule le revenu total généré par ce produit
        from sales.models import OrderItem
        return OrderItem.objects.filter(product=obj).aggregate(Sum('subtotal'))['subtotal__sum'] or 0