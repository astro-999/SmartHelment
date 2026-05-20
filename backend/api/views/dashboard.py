from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta

from ..models import HelmetDevice, SensorReading, GPSLocation, Alert
from ..serializers import (
    HelmetDeviceSerializer, GPSLocationSerializer,
    AlertSerializer, SensorReadingSerializer,
)


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
