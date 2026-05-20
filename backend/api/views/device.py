from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import EmergencyContact, HelmetDevice, SensorReading, GPSLocation
from ..serializers import (
    EmergencyContactSerializer, HelmetDeviceSerializer,
    SensorDataInputSerializer, GPSInputSerializer, GPSLocationSerializer,
    SensorReadingSerializer,
)
from ..utils import broadcast_to_dashboard


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
