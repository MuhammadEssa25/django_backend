from rest_framework import serializers
from .models import Order, OrderItem, Payment
from products.serializers import ProductSerializer
from products.models import Product
from carts.models import Cart

class OrderItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_details', 'quantity', 'price', 'subtotal']
        read_only_fields = ['product_details', 'subtotal']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'payment_method', 'status', 'transaction_id', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'customer_username', 'created_at', 'updated_at', 
                 'status', 'total_amount', 'items', 'payment', 'shipping_address', 
                 'tracking_number', 'notes']
        read_only_fields = ['customer', 'created_at', 'updated_at']

class OrderCreateSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(required=True)
    payment_method = serializers.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        required=True
    )
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """Validate that the user has items in their cart"""
        user = self.context['request'].user
        
        try:
            cart = Cart.objects.get(customer=user)
            if cart.items.count() == 0:
                raise serializers.ValidationError("Your cart is empty. Add items before checkout.")
        except Cart.DoesNotExist:
            raise serializers.ValidationError("You don't have a cart. Add items before checkout.")
        
        # Check stock availability for all items
        for cart_item in cart.items.all():
            if cart_item.product.stock < cart_item.quantity:
                raise serializers.ValidationError(
                    f"Not enough stock for {cart_item.product.name}. Available: {cart_item.product.stock}"
                )
        
        return data

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status', 'tracking_number', 'notes']

