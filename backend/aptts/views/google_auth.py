import requests
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import random
import string

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def google_oauth_login(request):
    id_token = request.data.get('id_token')

    if not id_token:
        return Response({'error': 'Missing ID token'}, status=status.HTTP_400_BAD_REQUEST)

    # Verify token with Google
    google_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
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
            last_name=' '.join(name.split(' ')[1:]),
        )

    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })
