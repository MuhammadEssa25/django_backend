import uuid

from rest_framework import viewsets, status
from rest_framework.decorators import action, parser_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django.db import transaction, connection, ProgrammingError

from .models import Product, ProductView, Review, ProductImage, Category
from .serializers import ProductSerializer, ProductCreateUpdateSerializer, ReviewSerializer, ProductImageSerializer, CategorySerializer
from permissions import IsSellerOrAdmin, IsProductSeller


class CategoryViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing category instances.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSellerOrAdmin()]
        return super().get_permissions()
    
    @extend_schema(
        description="List all categories",
        responses={200: CategorySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        print("CategoryViewSet.list() called")  # Debug print
        print(f"Request path: {request.path}")  # Print the request path
        print(f"Request method: {request.method}")  # Print the request method
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        description="Create a new category",
        request=CategorySerializer,
        responses={201: CategorySerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        description="Retrieve a specific category by ID",
        responses={200: CategorySerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        description="Update a category (full update)",
        request=CategorySerializer,
        responses={200: CategorySerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        description="Update a category (partial update)",
        request=CategorySerializer,
        responses={200: CategorySerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if category has products
        if instance.products.exists():
            return Response(
                {'error': 'Cannot delete category that has products. Reassign products to another category first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use a custom deletion method to avoid cascade issues with missing tables
        try:
            # Get the category ID before deleting
            category_id = instance.id
            
            # Use raw SQL to delete the category directly, avoiding Django's ORM cascade
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM products_category WHERE id = %s", [category_id])
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'error': f'Failed to delete category: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        description="Get all subcategories for a specific category",
        responses={200: CategorySerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def subcategories(self, request, pk=None):
        """
        Get all subcategories for a specific category
        """
        category = self.get_object()
        subcategories = Category.objects.filter(parent=category)
        serializer = self.get_serializer(subcategories, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="Get all products in a specific category",
        responses={200: ProductSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """
        Get all products in a specific category
        """
        category = self.get_object()
        products = category.products.all()
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsProductSeller]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated(), IsSellerOrAdmin()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsProductSeller()]
        return super().get_permissions()
    
    def get_queryset(self):
        user = self.request.user
        # Admins and staff can see all products
        if user.is_authenticated and (user.is_staff or user.role == 'admin'):
            return Product.objects.all()
        # Sellers can see their own products
        elif user.is_authenticated and user.role == 'seller':
            return Product.objects.filter(seller=user)
        # Everyone else can see all products (for browsing)
        return Product.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Track view - safely handle session
        try:
            if request.user.is_authenticated:
                # Check if ProductView table exists before creating a record
                if self._table_exists('products_productview'):
                    ProductView.objects.create(product=instance, user=request.user)
            else:
                session_id = request.session.get('session_id')
                if not session_id:
                    session_id = str(uuid.uuid4())
                    request.session['session_id'] = session_id
                # Check if ProductView table exists before creating a record
                if self._table_exists('products_productview'):
                    ProductView.objects.create(product=instance, session_id=session_id)
        except Exception:
            # Don't let view tracking failure affect the API response
            pass
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def _table_exists(self, table_name):
        """Check if a table exists in the database"""
        with connection.cursor() as cursor:
            tables = connection.introspection.table_names()
            return table_name in tables
    
    def _safe_delete_related(self, model_class, filter_kwargs):
        """Safely delete related objects, handling the case where the table doesn't exist"""
        try:
            model_class.objects.filter(**filter_kwargs).delete()
        except ProgrammingError:
            # Table doesn't exist, so nothing to delete
            pass
    
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'price': {'type': 'number'},
                    'discount_price': {'type': 'number', 'nullable': True},
                    'stock': {'type': 'integer'},
                    'category': {'type': 'integer'},
                    'images': {
                        'type': 'array',
                        'items': {'type': 'string', 'format': 'binary'}
                    },
                },
                'required': ['name', 'description', 'price', 'stock', 'category']
            }
        },
        parameters=[
            OpenApiParameter(
                name='images',
                type=OpenApiTypes.BINARY,
                location='form',
                description='Product images (max 8)',
                many=True,
                required=False,
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        # Handle regular fields with serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        
        # Handle image uploads separately
        images = request.FILES.getlist('images')
        if images:
            for image in images:
                # Check if product already has 8 images
                if product.images.count() >= 8:
                    break
                    
                # Check file extension
                import os
                ext = os.path.splitext(image.name)[1].lower()
                if ext not in ['.jpg', '.jpeg', '.png']:
                    continue
                    
                ProductImage.objects.create(product=product, image=image)
        
        # Return the full product data
        return Response(
            ProductSerializer(product, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'price': {'type': 'number'},
                    'discount_price': {'type': 'number', 'nullable': True},
                    'stock': {'type': 'integer'},
                    'category': {'type': 'integer'},
                    'images': {
                        'type': 'array',
                        'items': {'type': 'string', 'format': 'binary'}
                    },
                }
            }
        },
        parameters=[
            OpenApiParameter(
                name='images',
                type=OpenApiTypes.BINARY,
                location='form',
                description='Product images (max 8)',
                many=True,
                required=False,
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        
        # Handle image uploads separately
        images = request.FILES.getlist('images')
        if images:
            for image in images:
                # Check if product already has 8 images
                if product.images.count() >= 8:
                    break
                    
                # Check file extension
                import os
                ext = os.path.splitext(image.name)[1].lower()
                if ext not in ['.jpg', '.jpeg', '.png']:
                    continue
                    
                ProductImage.objects.create(product=product, image=image)
        
        # Return the full product data
        return Response(
            ProductSerializer(product, context={'request': request}).data
        )
    
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'price': {'type': 'number'},
                    'discount_price': {'type': 'number', 'nullable': True},
                    'stock': {'type': 'integer'},
                    'category': {'type': 'integer'},
                    'images': {
                        'type': 'array',
                        'items': {'type': 'string', 'format': 'binary'}
                    },
                }
            }
        },
        parameters=[
            OpenApiParameter(
                name='images',
                type=OpenApiTypes.BINARY,
                location='form',
                description='Product images (max 8)',
                many=True,
                required=False,
            ),
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if user is the seller
        if instance.seller != request.user and not request.user.is_staff and request.user.role != 'admin':
            return Response(
                {'error': 'Only the seller or admin can delete this product'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get the product ID before deleting
        product_id = instance.id
        
        # Use raw SQL to delete the product and its related objects
        # This completely bypasses Django's ORM and its cascading delete mechanism
        with connection.cursor() as cursor:
            # First delete related objects that we know exist
            try:
                # Delete ProductImage records
                cursor.execute("DELETE FROM products_productimage WHERE product_id = %s", [product_id])
            except Exception:
                # Ignore errors if table doesn't exist
                pass
                
            try:
                # Delete Review records
                cursor.execute("DELETE FROM products_review WHERE product_id = %s", [product_id])
            except Exception:
                # Ignore errors if table doesn't exist
                pass
                
            # Finally delete the product itself
            cursor.execute("DELETE FROM products_product WHERE id = %s", [product_id])
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_review(self, request, pk=None):
        product = self.get_object()
        serializer = ReviewSerializer(data=request.data)
        
        if serializer.is_valid():
            # Check if user already reviewed this product
            existing_review = Review.objects.filter(user=request.user, product=product).first()
            if existing_review:
                return Response(
                    {'error': 'You have already reviewed this product'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save(user=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'images': {
                        'type': 'array',
                        'items': {'type': 'string', 'format': 'binary'}
                    },
                },
                'required': ['images']
            }
        },
        parameters=[
            OpenApiParameter(
                name='images',
                type=OpenApiTypes.BINARY,
                location='form',
                description='Product images (max 8)',
                many=True,
                required=True,
            ),
        ],
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsProductSeller], parser_classes=[MultiPartParser, FormParser])
    def upload_images(self, request, pk=None):
        product = self.get_object()
        
        # Check if user is the seller
        if product.seller != request.user and not request.user.is_staff and request.user.role != 'admin':
            return Response(
                {'error': 'Only the seller or admin can upload images for this product'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        images = request.FILES.getlist('images')
        if not images:
            return Response(
                {'error': 'No images provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if adding these images would exceed the limit
        current_count = product.images.count()
        if current_count + len(images) > 8:
            return Response(
                {'error': f'A product can have at most 8 images. You already have {current_count} images.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process each image
        created_images = []
        for image in images:
            # Validate file extension
            import os
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png']:
                return Response(
                    {'error': f'File {image.name} is not a valid image format. Only JPG and PNG are allowed.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create the image
            product_image = ProductImage.objects.create(product=product, image=image)
            created_images.append(ProductImageSerializer(product_image, context={'request': request}).data)
        
        return Response(created_images, status=status.HTTP_201_CREATED)

