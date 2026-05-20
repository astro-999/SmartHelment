from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from ..models import HelmetDevice, Alert
from ..serializers import AlertSerializer, AlertInputSerializer
from ..utils import broadcast_to_dashboard


# ============ ALERT CREATE (ESP32 Endpoint) ============

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


# ============ ALERT ACTIONS ============

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
