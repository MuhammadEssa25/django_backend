from django.urls import path
from .views import ProductViewSet, CategoryViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Debug view to check if the URL routing is working
@api_view(['GET'])
def debug_view(request):
    return Response({"message": "Debug view is working!"})

# Define URL patterns explicitly
urlpatterns = [
    # Debug route
    path('debug/', debug_view, name='debug'),
    
    # Product routes
    path('', ProductViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='product-list'),
    
    path('<int:pk>/', ProductViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='product-detail'),
    
    # Category routes
    path('categories/', CategoryViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='category-list'),
    
    path('categories/<int:pk>/', CategoryViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='category-detail'),
    
    # Category custom actions
    path('categories/<int:pk>/subcategories/', CategoryViewSet.as_view({
        'get': 'subcategories'
    }), name='category-subcategories'),
    
    path('categories/<int:pk>/products/', CategoryViewSet.as_view({
        'get': 'products'
    }), name='category-products'),
    
    # Product custom actions
    path('<int:pk>/add-review/', ProductViewSet.as_view({
        'post': 'add_review'
    }), name='product-add-review'),
    
    path('<int:pk>/upload-images/', ProductViewSet.as_view({
        'post': 'upload_images'
    }), name='product-upload-images'),
]

