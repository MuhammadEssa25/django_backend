from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Order, OrderItem, Payment
from .serializers import OrderSerializer, OrderItemSerializer, PaymentSerializer
from analytics.models import UserActivity

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

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

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)
        
    def create(self, request, *args, **kwargs):
        # Get order data
        order_data = request.data
        items_data = order_data.pop('items', [])
        
        # Create order
        serializer = self.get_serializer(data=order_data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(customer=request.user)
        
        # Create order items
        for item_data in items_data:
            item_data['order'] = order.id
            item_serializer = OrderItemSerializer(data=item_data)
            item_serializer.is_valid(raise_exception=True)
            item_serializer.save()
            
            # Track purchase activity
            try:
                UserActivity.objects.create(
                    user=request.user,
                    activity_type='purchase',
                    product_id=item_data['product']
                )
            except Exception:
                # Don't let activity tracking failure affect the order creation
                pass
        
        # Return the complete order
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return OrderItem.objects.all()
        elif user.role == 'seller':
            return OrderItem.objects.filter(product__seller=user)
        else:
            return OrderItem.objects.filter(order__customer=user)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return Payment.objects.all()
        return Payment.objects.filter(order__customer=user)
