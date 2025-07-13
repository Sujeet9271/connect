import jwt
from datetime import datetime, timedelta
from django.conf import settings
from decouple import config

import time
from django.core.cache import cache
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

INACTIVITY_LIMIT_SECONDS = config('INACTIVITY_LIMIT_MINUTES', default=15, cast=int) * 60  # 15 minutes

class InactivityJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        user_auth_tuple = super().authenticate(request)
        if user_auth_tuple is None:
            return None

        user, token = user_auth_tuple
        user_id = user.id
        now = int(time.time())
        cache_key = f"user_last_active:{user_id}"
        last_active = cache.get(cache_key)

        if last_active and (now - last_active) > INACTIVITY_LIMIT_SECONDS:
            raise AuthenticationFailed("Session expired due to inactivity.")

        # Update last activity time
        cache.set(cache_key, now, timeout=24 * 60 * 60)  # Keep for 24 hours
        return user, token