from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count
from products.models import Product, Category, ProductView
from django.db.models.functions import TruncDay
from datetime import timedelta
from django.utils import timezone

@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_stats(request):
    """Get dashboard statistics for admin"""
    # Time range
    days = int(request.query_params.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Product views over time
    views_by_day = ProductView.objects.filter(
        timestamp__gte=start_date
    ).annotate(
        day=TruncDay('timestamp')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Top products
    top_products = Product.objects.annotate(
        view_count=Count('views')
    ).order_by('-view_count')[:10].values('id', 'name')
    
    # Add view count to each product
    for product in top_products:
        product['view_count'] = ProductView.objects.filter(product_id=product['id']).count()
    
    # Top categories
    top_categories = Category.objects.annotate(
        product_count=Count('products')
    ).order_by('-product_count')[:10].values('id', 'name')
    
    # Add product count to each category
    for category in top_categories:
        category['product_count'] = Product.objects.filter(category_id=category['id']).count()
    
    return Response({
        'views_by_day': list(views_by_day),
        'top_products': list(top_products),
        'top_categories': list(top_categories),
    })
