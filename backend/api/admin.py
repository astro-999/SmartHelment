from django.contrib import admin
from .models import EmergencyContact, HelmetDevice, SensorReading, GPSLocation, Alert


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'user', 'relationship', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('name', 'phone')


@admin.register(HelmetDevice)
class HelmetDeviceAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'name', 'user', 'status', 'battery_level', 'last_seen')
    list_filter = ('status',)
    search_fields = ('device_id', 'name')
    readonly_fields = ('last_seen', 'created_at')


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ('device', 'timestamp', 'acc_x', 'acc_y', 'acc_z')
    list_filter = ('device',)
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'


@admin.register(GPSLocation)
class GPSLocationAdmin(admin.ModelAdmin):
    list_display = ('device', 'timestamp', 'latitude', 'longitude', 'speed')
    list_filter = ('device',)
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('alert_type', 'severity', 'status', 'device', 'created_at')
    list_filter = ('alert_type', 'severity', 'status')
    search_fields = ('message',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
