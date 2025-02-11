from django.contrib import admin
from .models import Analytics

@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ['seller', 'total_sales', 'total_orders', 'date']
    list_filter = ['date', 'seller']
    search_fields = ['seller__username']

