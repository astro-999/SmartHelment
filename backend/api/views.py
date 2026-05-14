from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import EmergencyContact, HelmetDevice, SensorReading, GPSLocation, Alert
from .serializers import (
    UserRegistrationSerializer, UserSerializer, EmergencyContactSerializer,
    HelmetDeviceSerializer, SensorReadingSerializer, SensorDataInputSerializer,
    GPSLocationSerializer, GPSInputSerializer, AlertSerializer, AlertInputSerializer,
)


def broadcast_to_dashboard(data_type, data):
    """Send real-time update to all connected dashboard clients."""
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "dashboard",
            {
                "type": "dashboard_update",
                "data_type": data_type,
                "data": data,
            }
        )
    except Exception:
        pass  # Don't fail if no WebSocket clients connected


# ============ AUTH ============

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class ProfileView(APIView):
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ============ EMERGENCY CONTACTS ============

class EmergencyContactViewSet(viewsets.ModelViewSet):
    serializer_class = EmergencyContactSerializer

    def get_queryset(self):
        return EmergencyContact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ============ DEVICE ============

class DeviceViewSet(viewsets.ModelViewSet):
    serializer_class = HelmetDeviceSerializer

    def get_queryset(self):
        return HelmetDevice.objects.filter(user=self.request.user)


# ============ SENSOR DATA (ESP32 Endpoint) ============

class SensorDataView(APIView):
    permission_classes = [permissions.AllowAny]  # ESP32 posts without JWT

    def post(self, request):
        serializer = SensorDataInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            device = HelmetDevice.objects.get(device_id=data['device_id'])
        except HelmetDevice.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

        device.status = 'online'
        device.save(update_fields=['status', 'last_seen'])

        reading = SensorReading.objects.create(
            device=device,
            acc_x=data['acc_x'],
            acc_y=data['acc_y'],
            acc_z=data['acc_z'],
            gyro_x=data.get('gyro_x', 0),
            gyro_y=data.get('gyro_y', 0),
            gyro_z=data.get('gyro_z', 0),
        )

        broadcast_to_dashboard('sensor', {
            'acc_x': data['acc_x'],
            'acc_y': data['acc_y'],
            'acc_z': data['acc_z'],
            'gyro_x': data.get('gyro_x', 0),
            'gyro_y': data.get('gyro_y', 0),
            'gyro_z': data.get('gyro_z', 0),
            'timestamp': reading.timestamp.isoformat(),
        })

        return Response({'status': 'ok', 'id': reading.id}, status=status.HTTP_201_CREATED)


# ============ GPS DATA (ESP32 Endpoint) ============

class GPSDataView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = GPSInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            device = HelmetDevice.objects.get(device_id=data['device_id'])
        except HelmetDevice.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

        location = GPSLocation.objects.create(
            device=device,
            latitude=data['latitude'],
            longitude=data['longitude'],
            speed=data.get('speed', 0),
            altitude=data.get('altitude', 0),
            accuracy=data.get('accuracy', 0),
        )

        broadcast_to_dashboard('gps', {
            'latitude': data['latitude'],
            'longitude': data['longitude'],
            'speed': data.get('speed', 0),
            'timestamp': location.timestamp.isoformat(),
        })

        return Response({'status': 'ok', 'id': location.id}, status=status.HTTP_201_CREATED)


# ============ ALERT (ESP32 Endpoint) ============

class AlertCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = AlertInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            device = HelmetDevice.objects.get(device_id=data['device_id'])
        except HelmetDevice.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

        alert = Alert.objects.create(
            device=device,
            alert_type=data['alert_type'],
            severity=data.get('severity', 'high'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            message=data.get('message', ''),
            acc_magnitude=data.get('acc_magnitude', 0),
        )

        broadcast_to_dashboard('alert', {
            'id': alert.id,
            'alert_type': alert.alert_type,
            'severity': alert.severity,
            'latitude': alert.latitude,
            'longitude': alert.longitude,
            'message': alert.message,
            'created_at': alert.created_at.isoformat(),
        })

        return Response(AlertSerializer(alert).data, status=status.HTTP_201_CREATED)


# ============ ALERTS LIST ============

class AlertListView(generics.ListAPIView):
    serializer_class = AlertSerializer

    def get_queryset(self):
        qs = Alert.objects.filter(device__user=self.request.user)
        alert_type = self.request.query_params.get('type')
        alert_status = self.request.query_params.get('status')
        if alert_type:
            qs = qs.filter(alert_type=alert_type)
        if alert_status:
            qs = qs.filter(status=alert_status)
        return qs


class AlertActionView(APIView):
    def post(self, request, pk, action_type):
        try:
            alert = Alert.objects.get(pk=pk, device__user=request.user)
        except Alert.DoesNotExist:
            return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)

        if action_type == 'resolve':
            alert.status = 'resolved'
            alert.resolved_at = timezone.now()
        elif action_type == 'cancel':
            alert.status = 'cancelled'
            alert.resolved_at = timezone.now()
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        alert.save()

        broadcast_to_dashboard('alert_update', {
            'id': alert.id,
            'status': alert.status,
        })

        return Response(AlertSerializer(alert).data)


# ============ DASHBOARD ============

class DashboardView(APIView):
    def get(self, request):
        device = HelmetDevice.objects.filter(user=request.user).first()
        if not device:
            return Response({'error': 'No device found'}, status=status.HTTP_404_NOT_FOUND)

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        latest_gps = GPSLocation.objects.filter(device=device).first()
        alerts = Alert.objects.filter(device=device)

        # Recent sensor readings (last 50)
        recent_readings = SensorReading.objects.filter(device=device)[:50]
        sensor_data = [{
            'timestamp': r.timestamp.isoformat(),
            'acc_x': r.acc_x, 'acc_y': r.acc_y, 'acc_z': r.acc_z,
            'gyro_x': r.gyro_x, 'gyro_y': r.gyro_y, 'gyro_z': r.gyro_z,
        } for r in reversed(list(recent_readings))]

        return Response({
            'device': HelmetDeviceSerializer(device).data,
            'latest_gps': GPSLocationSerializer(latest_gps).data if latest_gps else None,
            'total_alerts': alerts.count(),
            'active_alerts': alerts.filter(status='active').count(),
            'alerts_today': alerts.filter(created_at__gte=today_start).count(),
            'latest_alerts': AlertSerializer(alerts[:10], many=True).data,
            'sensor_data': sensor_data,
        })


# ============ SENSOR HISTORY ============

class SensorHistoryView(APIView):
    def get(self, request):
        device = HelmetDevice.objects.filter(user=request.user).first()
        if not device:
            return Response({'error': 'No device found'}, status=status.HTTP_404_NOT_FOUND)

        hours = int(request.query_params.get('hours', 1))
        since = timezone.now() - timedelta(hours=hours)

        readings = SensorReading.objects.filter(
            device=device,
            timestamp__gte=since
        ).order_by('timestamp')[:500]

        return Response(SensorReadingSerializer(readings, many=True).data)


# ============ GPS HISTORY ============

class GPSHistoryView(APIView):
    def get(self, request):
        device = HelmetDevice.objects.filter(user=request.user).first()
        if not device:
            return Response({'error': 'No device found'}, status=status.HTTP_404_NOT_FOUND)

        hours = int(request.query_params.get('hours', 1))
        since = timezone.now() - timedelta(hours=hours)

        locations = GPSLocation.objects.filter(
            device=device,
            timestamp__gte=since
        ).order_by('timestamp')[:200]

        return Response(GPSLocationSerializer(locations, many=True).data)


# ============ SOS TRIGGER ============

class SOSTriggerView(APIView):
    def post(self, request):
        device = HelmetDevice.objects.filter(user=request.user).first()
        if not device:
            return Response({'error': 'No device found'}, status=status.HTTP_404_NOT_FOUND)

        latest_gps = GPSLocation.objects.filter(device=device).first()

        alert = Alert.objects.create(
            device=device,
            alert_type='sos',
            severity='critical',
            latitude=latest_gps.latitude if latest_gps else None,
            longitude=latest_gps.longitude if latest_gps else None,
            message='SOS triggered from web app!',
        )

        broadcast_to_dashboard('alert', {
            'id': alert.id,
            'alert_type': 'sos',
            'severity': 'critical',
            'latitude': alert.latitude,
            'longitude': alert.longitude,
            'message': alert.message,
            'created_at': alert.created_at.isoformat(),
        })

        contacts = EmergencyContact.objects.filter(user=request.user)

        return Response({
            'alert': AlertSerializer(alert).data,
            'contacts_notified': EmergencyContactSerializer(contacts, many=True).data,
            'message': 'SOS alert created. Emergency contacts notified.',
        }, status=status.HTTP_201_CREATED)
