from rest_framework import serializers
from django.db.models import Avg
from .models import Product, Category, ProductImage, Review

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent']

class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url']
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
    
    def validate_image(self, value):
        import os
        from django.core.exceptions import ValidationError
        
        # Check file extension
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png']:
            raise serializers.ValidationError('Only JPG and PNG files are allowed.')
            
        # Check file size (limit to 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('Image size cannot exceed 5MB.')
            
        return value

class ReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'user_username', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'discount_price', 
            'stock', 'category', 'category_name', 'seller', 'seller_username', 
            'created_at', 'updated_at', 'images', 'reviews', 'average_rating'
        ]
        read_only_fields = ['seller', 'created_at', 'updated_at']
    
    def get_average_rating(self, obj):
        avg = obj.reviews.aggregate(avg_rating=Avg('rating'))
        return avg['avg_rating'] or 0

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'discount_price', 'stock', 'category']
    
    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user
        product = super().create(validated_data)
        return product

