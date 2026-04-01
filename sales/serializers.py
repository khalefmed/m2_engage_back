from rest_framework import serializers
from .models import Order, OrderItem
from clients.serializers import CustomerSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price', 'subtotal']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    client_details = CustomerSerializer(source='client', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'client', 'client_details', 'total_amount', 'items', 'created_at']