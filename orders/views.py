from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem, Payment
from .serializers import (
    OrderSerializer, OrderItemSerializer, PaymentSerializer, 
    OrderCreateSerializer, OrderStatusUpdateSerializer
)
from carts.models import Cart
from products.models import Product
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

class OrderViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    """
    Order API - only exposes list, retrieve, and specific actions
    """
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'checkout':
            return OrderCreateSerializer
        elif self.action == 'update_status':
            return OrderStatusUpdateSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return Order.objects.all()
        elif user.role == 'seller':
            # Get orders that contain products sold by this seller
            return Order.objects.filter(items__product__seller=user).distinct()
        else:
            # Regular customers can only see their own orders
            return Order.objects.filter(customer=user)
    
    @extend_schema(
        request=OpenApiTypes.OBJECT,
        parameters=[
            OpenApiParameter(
                name='shipping_address',
                description='Shipping address for the order',
                required=True,
                type=str,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='payment_method',
                description='Payment method (credit_card, paypal, bank_transfer)',
                required=True,
                type=str,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='notes',
                description='Additional notes for the order',
                required=False,
                type=str,
                location=OpenApiParameter.QUERY
            ),
        ],
        examples=[
            OpenApiExample(
                'Example Request',
                value={
                    'shipping_address': '123 Main St, City, Country',
                    'payment_method': 'credit_card',
                    'notes': 'Please deliver in the evening'
                },
                request_only=True,
            ),
        ],
        description='Create an order from the items in the cart'
    )
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def checkout(self, request):
        """Convert cart to order"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        # Get user's cart
        cart = get_object_or_404(Cart, customer=user)
        
        # Ensure cart is not empty
        if cart.items.count() == 0:
            return Response(
                {"error": "Your cart is empty. Add items before checkout."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create order
        order = Order.objects.create(
            customer=user,
            total_amount=cart.total_amount,
            status='pending',
            shipping_address=serializer.validated_data.get('shipping_address'),
            notes=serializer.validated_data.get('notes', '')
        )
        
        # Create order items from cart items
        for cart_item in cart.items.all():
            # Check stock one more time
            if cart_item.product.stock < cart_item.quantity:
                # Rollback transaction
                transaction.set_rollback(True)
                return Response(
                    {"error": f"Not enough stock for {cart_item.product.name}. Available: {cart_item.product.stock}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create order item
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            
            # Update product stock
            product = cart_item.product
            product.stock -= cart_item.quantity
            product.save()
        
        # Create payment record
        Payment.objects.create(
            order=order,
            amount=order.total_amount,
            payment_method=serializer.validated_data.get('payment_method'),
            status='pending'
        )
        
        # Clear the cart after successful order creation
        cart.items.all().delete()
        
        # Return the complete order
        return Response(
            OrderSerializer(order, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        request=OrderStatusUpdateSerializer,
        description='Update the status of an order (for sellers and admins)'
    )
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update order status (for sellers and admins)"""
        order = self.get_object()
        
        # Only sellers of products in this order and admins can update status
        user = request.user
        if not (user.is_staff or user.role == 'admin'):
            # Check if user is seller of any product in this order
            seller_products = order.items.filter(product__seller=user).exists()
            if not seller_products:
                return Response(
                    {"error": "You don't have permission to update this order."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(OrderSerializer(order).data)
    
    @extend_schema(
        description='Cancel an order (only available for pending or processing orders)'
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order"""
        order = self.get_object()
        
        # Only the customer or admin can cancel an order
        if not (request.user == order.customer or request.user.is_staff or request.user.role == 'admin'):
            return Response(
                {"error": "You don't have permission to cancel this order."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Can only cancel if order is pending or processing
        if order.status not in ['pending', 'processing']:
            return Response(
                {"error": f"Cannot cancel order with status '{order.status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update order status
        order.status = 'cancelled'
        order.save()
        
        # Restore product stock
        for item in order.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()
        
        # Update payment status if exists
        try:
            payment = order.payment
            payment.status = 'failed'
            payment.save()
        except Payment.DoesNotExist:
            pass
        
        return Response(OrderSerializer(order).data)

