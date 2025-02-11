from rest_framework import viewsets, permissions
from .models import Analytics
from .serializers import AnalyticsSerializer

class AnalyticsViewSet(viewsets.ModelViewSet):
    queryset = Analytics.objects.all()
    serializer_class = AnalyticsSerializer
 #   permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Analytics.objects.all()
        elif user.role == 'seller':
            return Analytics.objects.filter(seller=user)
        else:
            return Analytics.objects.none()

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)