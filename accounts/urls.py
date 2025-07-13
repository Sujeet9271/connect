from django.urls import include, path
from rest_framework.routers import DefaultRouter
from accounts import views

app_name = 'accounts'

accounts_router = DefaultRouter()
accounts_router.register(r'users', views.UserViewSet, basename='users')
accounts_router.register(r'connections', views.ConnectionRequestViewSet, basename='connections')


urlpatterns = [
    path('signup/', views.register_view, name='signup'),
    path('token/access/', views.token_obtain_pair_view, name='access_token'),
    path('token/refresh/', views.token_refresh,name="token_refresh"),
    path('token/verify/', views.token_verify,name="token_verify"),
    path('profile/', views.user_profile, name='user_profile'),
    path('connections/<int:id>/', views.connection_actions, name='connection_actions'),
    path('confirm/<uidb64>/<token>/', views.activate_user, name='activate_user'),
]