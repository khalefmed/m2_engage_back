from rest_framework import serializers
from .models import Customer
from django.db.models import Sum

class CustomerSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()
    total_spent = serializers.SerializerMethodField()
    total_orders = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 
            'gender', 'date_of_birth', 'age', 'profession',
            'country', 'city', 'address', 'latitude', 'longitude',
            'total_spent', 'total_orders', 'created_at'
        ]

    def get_total_spent(self, obj):
        # On utilise l'agrégation pour la performance
        return obj.orders.aggregate(total=Sum('total_amount'))['total'] or 0

    def get_total_orders(self, obj):
        return obj.orders.count()