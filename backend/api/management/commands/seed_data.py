"""
Seed initial data for SmartHelmetX development and testing.
Usage: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import HelmetDevice, EmergencyContact


class Command(BaseCommand):
    help = 'Seed initial test data for SmartHelmetX development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Delete existing test data before seeding',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('Resetting test data...'))
            User.objects.filter(username__in=['admin', 'ast']).delete()

        # --- Create admin user ---
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@test.com',
                'first_name': 'Smart',
                'last_name': 'Rider',
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS("Created user 'admin' (password: admin123)"))
        else:
            self.stdout.write("User 'admin' already exists.")

        # --- Ensure admin has a device ---
        device, created = HelmetDevice.objects.get_or_create(
            device_id='SHX-0001',
            defaults={
                'user': admin,
                'name': 'SmartHelmetX',
                'status': 'online',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created device SHX-0001"))
        else:
            device.status = 'online'
            device.save(update_fields=['status', 'last_seen'])
            self.stdout.write("Device SHX-0001 already exists — set to online.")

        # --- Ensure admin has emergency contact ---
        contact, created = EmergencyContact.objects.get_or_create(
            user=admin,
            is_primary=True,
            defaults={
                'name': 'Emergency Contact',
                'phone': '+97798XXXXXXXX',
                'relationship': 'Family',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created emergency contact for admin"))
        else:
            self.stdout.write("Emergency contact already exists.")

        # --- Summary ---
        self.stdout.write('')
        for u in User.objects.all():
            devices = list(HelmetDevice.objects.filter(user=u).values_list('device_id', flat=True))
            contacts_count = EmergencyContact.objects.filter(user=u).count()
            self.stdout.write(
                f"  User: {u.username} (id={u.id}) → "
                f"devices={devices}, contacts={contacts_count}"
            )

        self.stdout.write(self.style.SUCCESS(
            "\nSeed complete! Login with: admin / admin123"
        ))
