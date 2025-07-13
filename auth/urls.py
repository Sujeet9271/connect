from django.urls import include, path
from accounts import views
from rest_framework_simplejwt.views import (
    TokenObtainSlidingView,
    TokenRefreshSlidingView,
)

app_name = 'auth'


urlpatterns = [
    path('token/access/', views.token_obtain_pair_view, name='access_token'),
    path('token/refresh/', views.token_refresh,name="token_refresh"),
    path('token/verify/', views.token_verify,name="token_verify"),
    path('token/access/sliding/', TokenObtainSlidingView.as_view(), name='token_obtain_pair'),
    path('token/refresh/sliding/', TokenRefreshSlidingView.as_view(), name='token_refresh'),
]