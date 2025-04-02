from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product
from products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_details', 'quantity', 'subtotal', 'added_at']
        read_only_fields = ['added_at', 'subtotal']
    
    def validate_product(self, value):
        """Validate that the product exists and has stock"""
        if value.stock <= 0:
            raise serializers.ValidationError(f"Product '{value.name}' is out of stock")
        return value
    
    def validate_quantity(self, value):
        """Validate that the quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero")
        return value
    
    def validate(self, data):
        """Validate that the requested quantity is available"""
        product = data.get('product')
        quantity = data.get('quantity', 1)
        
        # If we're updating an existing cart item, we need to check the current quantity
        if self.instance:
            if product.stock < quantity:
                raise serializers.ValidationError(f"Not enough stock. Only {product.stock} available.")
        else:
            if product.stock < quantity:
                raise serializers.ValidationError(f"Not enough stock. Only {product.stock} available.")
        
        return data

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'customer', 'items', 'total_amount', 'item_count', 'created_at', 'updated_at']
        read_only_fields = ['customer', 'created_at', 'updated_at']

