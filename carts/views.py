from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
import logging

# Set up logger
logger = logging.getLogger(__name__)

class CartViewSet(viewsets.GenericViewSet):
    """
    Cart API - only exposes specific actions, not the full ModelViewSet
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Users can only see their own cart"""
        return Cart.objects.filter(customer=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        """Get or create the user's cart"""
        cart, created = Cart.objects.get_or_create(customer=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @extend_schema(
        request=OpenApiTypes.OBJECT,
        parameters=[
            OpenApiParameter(
                name='product',
                description='Product ID to add to cart',
                required=True,
                type=int,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='quantity',
                description='Quantity to add (default: 1)',
                required=False,
                type=int,
                location=OpenApiParameter.QUERY
            ),
        ],
        examples=[
            OpenApiExample(
                'Example Request',
                value={
                    'product': 1,
                    'quantity': 2
                },
                request_only=True,
            ),
        ],
        description='Add a product to the user\'s cart'
    )
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add an item to the user's cart"""
        try:
            # Get or create the cart
            cart, created = Cart.objects.get_or_create(customer=request.user)
            
            # Get product and quantity from request
            product_id = request.data.get('product')
            if not product_id:
                return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                quantity = int(request.data.get('quantity', 1))
                if quantity <= 0:
                    return Response({"error": "Quantity must be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({"error": "Quantity must be a valid number"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the product
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({"error": f"Product with ID {product_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if product is in stock
            if product.stock < quantity:
                return Response(
                    {"error": f"Not enough stock. Only {product.stock} available."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if item already exists in cart
            try:
                cart_item = CartItem.objects.get(cart=cart, product=product)
                # Update quantity
                cart_item.quantity += quantity
                # Validate stock again
                if product.stock < cart_item.quantity:
                    return Response(
                        {"error": f"Not enough stock. Only {product.stock} available."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                cart_item.save()
                logger.info(f"Updated cart item: {cart_item.id}, product: {product.id}, quantity: {cart_item.quantity}")
            except CartItem.DoesNotExist:
                # Create new cart item
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=quantity
                )
                logger.info(f"Created new cart item: {cart_item.id}, product: {product.id}, quantity: {quantity}")
            
            # Return updated cart
            cart.refresh_from_db()  # Refresh to ensure we get the latest data
            serializer = self.get_serializer(cart)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error adding item to cart: {str(e)}")
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        request=OpenApiTypes.OBJECT,
        parameters=[
            OpenApiParameter(
                name='item_id',
                description='Cart item ID to update',
                required=True,
                type=int,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='quantity',
                description='New quantity',
                required=True,
                type=int,
                location=OpenApiParameter.QUERY
            ),
        ],
        examples=[
            OpenApiExample(
                'Example Request',
                value={
                    'item_id': 1,
                    'quantity': 3
                },
                request_only=True,
            ),
        ],
        description='Update the quantity of an item in the cart'
    )
    @action(detail=False, methods=['post'])
    def update_item(self, request):
        """Update quantity of an item in the cart"""
        try:
            cart = get_object_or_404(Cart, customer=request.user)
            
            item_id = request.data.get('item_id')
            if not item_id:
                return Response({"error": "Item ID is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                quantity = int(request.data.get('quantity', 1))
                if quantity <= 0:
                    return Response({"error": "Quantity must be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({"error": "Quantity must be a valid number"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the cart item
            try:
                cart_item = CartItem.objects.get(id=item_id, cart=cart)
            except CartItem.DoesNotExist:
                return Response({"error": f"Cart item with ID {item_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if product is in stock
            if cart_item.product.stock < quantity:
                return Response(
                    {"error": f"Not enough stock. Only {cart_item.product.stock} available."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update quantity
            cart_item.quantity = quantity
            cart_item.save()
            logger.info(f"Updated cart item: {cart_item.id}, quantity: {quantity}")
            
            # Return updated cart
            cart.refresh_from_db()  # Refresh to ensure we get the latest data
            serializer = self.get_serializer(cart)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error updating cart item: {str(e)}")
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        request=OpenApiTypes.OBJECT,
        parameters=[
            OpenApiParameter(
                name='item_id',
                description='Cart item ID to remove',
                required=True,
                type=int,
                location=OpenApiParameter.QUERY
            ),
        ],
        examples=[
            OpenApiExample(
                'Example Request',
                value={
                    'item_id': 1
                },
                request_only=True,
            ),
        ],
        description='Remove an item from the cart'
    )
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove an item from the cart"""
        try:
            cart = get_object_or_404(Cart, customer=request.user)
            
            item_id = request.data.get('item_id')
            if not item_id:
                return Response({"error": "Item ID is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get and delete the cart item
            try:
                cart_item = CartItem.objects.get(id=item_id, cart=cart)
                cart_item.delete()
                logger.info(f"Removed cart item: {item_id}")
            except CartItem.DoesNotExist:
                return Response({"error": f"Cart item with ID {item_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
            
            # Return updated cart
            cart.refresh_from_db()  # Refresh to ensure we get the latest data
            serializer = self.get_serializer(cart)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error removing cart item: {str(e)}")
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear all items from the cart"""
        try:
            cart = get_object_or_404(Cart, customer=request.user)
            cart.items.all().delete()
            logger.info(f"Cleared cart for user: {request.user.id}")
            
            # Return empty cart
            cart.refresh_from_db()  # Refresh to ensure we get the latest data
            serializer = self.get_serializer(cart)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error clearing cart: {str(e)}")
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

