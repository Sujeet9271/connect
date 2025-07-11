from rest_framework.authentication import BaseAuthentication
from django.contrib.auth import get_user_model
from rest_framework import exceptions
from auth.authentication import decode_jwt

User = get_user_model()

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            prefix, token = auth_header.split()
            if prefix.lower() != 'bearer':
                return None
        except ValueError:
            return None

        payload = decode_jwt(token)
        if not payload:
            raise exceptions.AuthenticationFailed('Invalid or expired token')

        try:
            user = User.objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')

        return (user, None)
