from django.urls import include, path
from accounts import views

app_name = 'auth'


urlpatterns = [
    path('token/access/', views.token_obtain_pair_view, name='access_token'),
    path('token/refresh/', views.token_refresh,name="token_refresh"),
    path('token/verify/', views.token_verify,name="token_verify"),
]