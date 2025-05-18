from rest_framework import viewsets, permissions, decorators, response, status
from django.contrib.auth import get_user_model, authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

from rest_framework_simplejwt.tokens import RefreshToken
import random
import string
import requests

from ..serializers.user_serializer import UserSerializer

User = get_user_model()

class IsAdminOrSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'destroy']:
            return [permissions.IsAdminUser()]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsAdminOrSelf()]
        return [permissions.AllowAny()]

    @decorators.action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return response.Response(serializer.data)

# Utility function to generate JWT for a user
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response(tokens, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user:
        tokens = get_tokens_for_user(user)
        return Response(tokens)
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    # With JWT, logout is handled client-side by deleting tokens
    return Response({'message': 'Logout: delete the tokens client-side'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    user = request.user
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    if not user.check_password(current_password):
        return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        validate_password(new_password, user)
    except ValidationError as e:
        return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)
    user.set_password(new_password)
    user.save()
    return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def google_login(request):
    id_token = request.data.get('id_token')

    if not id_token:
        return Response({'error': 'Missing id_token'}, status=status.HTTP_400_BAD_REQUEST)

    google_url = f'https://oauth2.googleapis.com/tokeninfo?id_token={id_token}'
    resp = requests.get(google_url)

    if resp.status_code != 200:
        return Response({'error': 'Invalid Google token'}, status=status.HTTP_400_BAD_REQUEST)

    user_data = resp.json()
    email = user_data.get('email')
    name = user_data.get('name', '')
    username_base = email.split('@')[0]

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        username = username_base
        while User.objects.filter(username=username).exists():
            suffix = ''.join(random.choices(string.digits, k=3))
            username = f"{username_base}{suffix}"
        user = User.objects.create_user(
            username=username,
            email=email,
            password=User.objects.make_random_password(),
            first_name=name.split(' ')[0],
            last_name=' '.join(name.split(' ')[1:])
        )

    tokens = get_tokens_for_user(user)
    return Response(tokens)
