from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import EmergencyContact, HelmetDevice, GPSLocation, Alert
from ..serializers import AlertSerializer, EmergencyContactSerializer
from ..utils import broadcast_to_dashboard


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
