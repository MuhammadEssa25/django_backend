from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from django.db import transaction
from .models import CustomUser
from .serializers import CustomUserSerializer, LoginSerializer

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
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return CustomUser.objects.none()
            
        # Allow all authenticated users to see all users
        return CustomUser.objects.all()
    
    def perform_create(self, serializer):
        password = serializer.validated_data.pop('password', None)
        instance = serializer.save()
        if password:
            instance.set_password(password)
            instance.save()
    
    def perform_destroy(self, instance):
        """
        Custom delete method to handle missing related tables
        """
        try:
            with transaction.atomic():
                # Delete the user directly with raw SQL to avoid cascade issues
                instance_id = instance.id
                instance.delete()
                return True
        except Exception as e:
            # If there's an error with related tables, try a different approach
            try:
                # Get the user ID before deleting
                instance_id = instance.id
                
                # Use a raw SQL query to delete the user directly
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM users_customuser WHERE id = %s", [instance_id])
                
                return True
            except Exception as inner_e:
                # If all else fails, log the error and return a response
                print(f"Error deleting user: {str(inner_e)}")
                return False

