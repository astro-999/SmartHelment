"""
SmartHelmetX project URL configuration.
"""
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # JWT token endpoints
    path('api/auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # All API endpoints defined in the api app
    path('api/', include('api.urls')),
]
