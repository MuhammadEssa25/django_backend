from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderItemViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'', OrderViewSet, basename='order')
router.register(r'items', OrderItemViewSet, basename='orderitem')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = router.urls

