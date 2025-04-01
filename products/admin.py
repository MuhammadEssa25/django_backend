from django.contrib import admin
from .models import Product, Category, ProductImage, Review

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 8  # Limit to 8 images
    fields = ['image']  # Removed is_primary field

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ['user', 'rating', 'comment', 'created_at']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'discount_price', 'stock', 'category', 'seller']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    inlines = [ProductImageInline, ReviewInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent']
    search_fields = ['name']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['comment']
    readonly_fields = ['product', 'user']

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product']  # Removed 'is_primary'
    # Removed list_filter
    search_fields = ['product__name']

