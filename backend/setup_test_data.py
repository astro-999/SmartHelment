import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'smarthelmet.settings'

import django
django.setup()

from django.contrib.auth.models import User
from api.models import HelmetDevice, EmergencyContact

# Create test user
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_user('admin', 'admin@test.com', 'admin123',
                                  first_name='Smart', last_name='Rider')
    print("User 'admin' created!")
else:
    u = User.objects.get(username='admin')
    print("User 'admin' already exists.")

# Create default device
if not HelmetDevice.objects.filter(device_id='SHX-0001').exists():
    HelmetDevice.objects.create(user=u, device_id='SHX-0001', name='SmartHelmetX', status='online')
    print("Device SHX-0001 created!")
else:
    print("Device SHX-0001 already exists.")

# Create sample emergency contact
if not EmergencyContact.objects.filter(user=u).exists():
    EmergencyContact.objects.create(user=u, name='Emergency Contact', phone='+97798XXXXXXXX',
                                     relationship='Family', is_primary=True)
    print("Emergency contact created!")

print("\nSetup complete! Login with: admin / admin123")
