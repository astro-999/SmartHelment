from rest_framework import serializers
from django.contrib.auth.models import User
from .models import EmergencyContact, HelmetDevice, SensorReading, GPSLocation, Alert


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2', 'first_name', 'last_name')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        # Create a default helmet device for the user
        HelmetDevice.objects.create(
            user=user,
            device_id=f'SHX-{user.id:04d}',
            name='SmartHelmetX'
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ('id', 'name', 'phone', 'relationship', 'is_primary', 'created_at')
        read_only_fields = ('id', 'created_at')


class HelmetDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelmetDevice
        fields = ('id', 'device_id', 'name', 'ble_mac', 'status', 'battery_level',
                  'firmware_version', 'fall_threshold', 'no_move_timeout', 'last_seen', 'created_at')
        read_only_fields = ('id', 'device_id', 'last_seen', 'created_at')


class SensorReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorReading
        fields = ('id', 'device', 'timestamp', 'acc_x', 'acc_y', 'acc_z',
                  'gyro_x', 'gyro_y', 'gyro_z')
        read_only_fields = ('id', 'timestamp')


class SensorDataInputSerializer(serializers.Serializer):
    """For ESP32 posting sensor data."""
    device_id = serializers.CharField()
    acc_x = serializers.FloatField()
    acc_y = serializers.FloatField()
    acc_z = serializers.FloatField()
    gyro_x = serializers.FloatField(default=0)
    gyro_y = serializers.FloatField(default=0)
    gyro_z = serializers.FloatField(default=0)


class GPSLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPSLocation
        fields = ('id', 'device', 'timestamp', 'latitude', 'longitude',
                  'speed', 'altitude', 'accuracy')
        read_only_fields = ('id', 'timestamp')


class GPSInputSerializer(serializers.Serializer):
    """For ESP32 posting GPS data."""
    device_id = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    speed = serializers.FloatField(default=0)
    altitude = serializers.FloatField(default=0)
    accuracy = serializers.FloatField(default=0)


class AlertSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    type_display = serializers.CharField(source='get_alert_type_display', read_only=True)

    class Meta:
        model = Alert
        fields = ('id', 'device', 'device_name', 'alert_type', 'type_display', 'status',
                  'severity', 'latitude', 'longitude', 'message', 'acc_magnitude',
                  'sms_sent', 'resolved_at', 'created_at')
        read_only_fields = ('id', 'created_at')


class AlertInputSerializer(serializers.Serializer):
    """For ESP32 posting alerts."""
    device_id = serializers.CharField()
    alert_type = serializers.ChoiceField(choices=['fall', 'sos', 'no_movement', 'impact'])
    severity = serializers.ChoiceField(choices=['low', 'medium', 'high', 'critical'], default='high')
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)
    message = serializers.CharField(default='')
    acc_magnitude = serializers.FloatField(default=0)


class DashboardSerializer(serializers.Serializer):
    """Dashboard summary data."""
    device = HelmetDeviceSerializer()
    latest_gps = GPSLocationSerializer(allow_null=True)
    total_alerts = serializers.IntegerField()
    active_alerts = serializers.IntegerField()
    alerts_today = serializers.IntegerField()
    latest_alerts = AlertSerializer(many=True)
    sensor_summary = serializers.DictField()
