from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views import (
    RegisterView, ProfileView,
    EmergencyContactViewSet, DeviceViewSet,
    SensorDataView, GPSDataView, AlertCreateView,
    AlertListView, AlertActionView,
    DashboardView, SensorHistoryView, GPSHistoryView,
    SOSTriggerView,
)

router = DefaultRouter()
router.register(r'contacts', EmergencyContactViewSet, basename='contact')
router.register(r'devices', DeviceViewSet, basename='device')

urlpatterns = [
    # Auth
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/profile/', ProfileView.as_view(), name='profile'),

    # CRUD endpoints
    path('api/', include(router.urls)),

    # ESP32 device endpoints (no auth required)
    path('api/sensor-data/', SensorDataView.as_view(), name='sensor-data'),
    path('api/gps/', GPSDataView.as_view(), name='gps-data'),
    path('api/alert/', AlertCreateView.as_view(), name='alert-create'),

    # Dashboard & history
    path('api/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('api/sensor-history/', SensorHistoryView.as_view(), name='sensor-history'),
    path('api/gps-history/', GPSHistoryView.as_view(), name='gps-history'),
    path('api/alerts/', AlertListView.as_view(), name='alert-list'),

    # Alert actions
    path('api/alerts/<int:pk>/<str:action_type>/', AlertActionView.as_view(), name='alert-action'),

    # SOS
    path('api/sos/', SOSTriggerView.as_view(), name='sos-trigger'),
]
