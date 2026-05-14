import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'smarthelmet.settings'
import django
django.setup()
from django.contrib.auth.models import User
from api.models import HelmetDevice, EmergencyContact

# Fix: ensure admin user has a device
admin = User.objects.get(username='admin')
if not HelmetDevice.objects.filter(user=admin).exists():
    HelmetDevice.objects.create(user=admin, device_id='SHX-0002', name='SmartHelmetX', status='online')
    print("Created device SHX-0002 for admin")

# Also ensure 'ast' user device is online
ast_device = HelmetDevice.objects.filter(device_id='SHX-0001').first()
if ast_device:
    ast_device.status = 'online'
    ast_device.save()
    print("Set SHX-0001 to online")

# Ensure admin has emergency contact
if not EmergencyContact.objects.filter(user=admin).exists():
    EmergencyContact.objects.create(user=admin, name='Emergency Contact', phone='+97798XXXXXXXX', relationship='Family', is_primary=True)
    print("Created emergency contact for admin")

# Print summary
for u in User.objects.all():
    devices = list(HelmetDevice.objects.filter(user=u).values_list('device_id', flat=True))
    print(f"User: {u.username} (id={u.id}) -> devices={devices}")

print("\nDone! Both users now have devices.")
print("Login as 'ast' (your account) or 'admin' / 'admin123'")
