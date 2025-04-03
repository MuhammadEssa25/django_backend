from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from django.db import transaction
from .models import CustomUser
from .serializers import CustomUserSerializer, LoginSerializer
from permissions import IsAdmin

@extend_schema(
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(
            description="Login successful",
            response={"type": "object", "properties": {
                "access": {"type": "string"},
                "refresh": {"type": "string"},
                "user": {"type": "object"}
            }}
        ),
        400: OpenApiResponse(description="Bad request"),
        401: OpenApiResponse(description="Invalid credentials"),
    },
    examples=[
        OpenApiExample(
            'Login Example',
            value={
                'username': 'testuser',
                'password': 'password123'
            },
            request_only=True,
        )
    ],
    description="Authenticate user and return JWT tokens"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """
    Authenticate user and return JWT tokens
    """
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    username = serializer.validated_data.get('username')
    password = serializer.validated_data.get('password')
    
    user = CustomUser.objects.filter(username=username).first()
    
    if user is None or not user.check_password(password):
        return Response(
            {'error': 'Invalid username or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': CustomUserSerializer(user).data
    })

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            if self.request.user.is_authenticated and self.request.user.role == 'admin':
                return [IsAuthenticated()]
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return CustomUser.objects.none()
            
        # Admin can see all users
        if user.is_staff or user.role == 'admin':
            return CustomUser.objects.all()
            
        # Regular users can only see themselves
        return CustomUser.objects.filter(id=user.id)
    
    def perform_create(self, serializer):
        password = serializer.validated_data.pop('password', None)
        instance = serializer.save()
        if password:
            instance.set_password(password)
            instance.save()
    
    def perform_update(self, serializer):
        password = serializer.validated_data.pop('password', None)
        instance = serializer.save()
        if password:
            instance.set_password(password)
            instance.save()
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get the current user's profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

