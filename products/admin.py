from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'regular_price', 'sale_price', 'stock', 'category', 'seller']
    list_filter = ['category', 'seller']
    search_fields = ['name', 'description']

