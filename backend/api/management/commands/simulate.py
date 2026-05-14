"""
Data simulator for SmartHelmetX.
Generates realistic sensor data, GPS movement, and occasional fall events.
Usage: python manage.py simulate
"""

import time
import math
import random
import requests
from django.core.management.base import BaseCommand


API_BASE = "http://127.0.0.1:8000/api"
DEVICE_ID = "SHX-0001"

# Kathmandu area coordinates
BASE_LAT = 27.7172
BASE_LNG = 85.3240


class Command(BaseCommand):
    help = 'Simulate SmartHelmetX sensor data for development'

    def add_arguments(self, parser):
        parser.add_argument('--interval', type=float, default=2.0,
                            help='Seconds between sensor readings (default: 2)')
        parser.add_argument('--fall-chance', type=float, default=0.02,
                            help='Probability of a fall event per reading (default: 0.02)')

    def handle(self, *args, **options):
        interval = options['interval']
        fall_chance = options['fall_chance']

        self.stdout.write(self.style.SUCCESS(
            f"\n[*] SmartHelmetX Simulator Started"
            f"\n    Device: {DEVICE_ID}"
            f"\n    Interval: {interval}s"
            f"\n    Fall chance: {fall_chance*100}%"
            f"\n    Press Ctrl+C to stop\n"
        ))

        t = 0
        lat = BASE_LAT
        lng = BASE_LNG
        heading = random.uniform(0, 360)
        speed = 0

        try:
            while True:
                t += interval

                # --- Simulate riding motion ---
                # Speed varies 0-60 km/h
                speed += random.uniform(-5, 5)
                speed = max(0, min(60, speed))

                # Move GPS position
                heading += random.uniform(-15, 15)
                rad = math.radians(heading)
                distance = (speed / 3600) * interval * 0.00001  # rough deg conversion
                lat += math.cos(rad) * distance
                lng += math.sin(rad) * distance

                # --- Normal sensor data (slight vibration) ---
                acc_x = random.gauss(0, 0.15)
                acc_y = random.gauss(0, 0.15)
                acc_z = random.gauss(1.0, 0.1)  # gravity
                gyro_x = random.gauss(0, 5)
                gyro_y = random.gauss(0, 5)
                gyro_z = random.gauss(0, 5)

                is_fall = random.random() < fall_chance

                if is_fall:
                    # Simulate fall: high acceleration spike
                    acc_x = random.uniform(2.0, 4.0) * random.choice([-1, 1])
                    acc_y = random.uniform(2.0, 4.0) * random.choice([-1, 1])
                    acc_z = random.uniform(0.1, 0.5)
                    gyro_x = random.uniform(100, 300)
                    gyro_y = random.uniform(100, 300)
                    speed = 0

                # --- POST sensor data ---
                try:
                    requests.post(f"{API_BASE}/sensor-data/", json={
                        "device_id": DEVICE_ID,
                        "acc_x": round(acc_x, 4),
                        "acc_y": round(acc_y, 4),
                        "acc_z": round(acc_z, 4),
                        "gyro_x": round(gyro_x, 2),
                        "gyro_y": round(gyro_y, 2),
                        "gyro_z": round(gyro_z, 2),
                    }, timeout=10)
                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                    self.stdout.write(self.style.WARNING("[!] Cannot connect to API server"))
                    time.sleep(interval)
                    continue

                # --- POST GPS data ---
                try:
                    requests.post(f"{API_BASE}/gps/", json={
                        "device_id": DEVICE_ID,
                        "latitude": round(lat, 6),
                        "longitude": round(lng, 6),
                        "speed": round(speed, 1),
                        "altitude": 1400 + random.uniform(-10, 10),
                        "accuracy": random.uniform(2, 10),
                    }, timeout=10)
                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                    pass

                # --- POST fall alert ---
                if is_fall:
                    mag = math.sqrt(acc_x**2 + acc_y**2 + acc_z**2)
                    alert_type = random.choice(['fall', 'impact'])
                    try:
                        requests.post(f"{API_BASE}/alert/", json={
                            "device_id": DEVICE_ID,
                            "alert_type": alert_type,
                            "severity": "critical" if mag > 3.5 else "high",
                            "latitude": round(lat, 6),
                            "longitude": round(lng, 6),
                            "message": f"{'Fall' if alert_type == 'fall' else 'High impact'} detected! G-force: {mag:.2f}g",
                            "acc_magnitude": round(mag, 2),
                        }, timeout=10)
                    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                        pass

                    self.stdout.write(self.style.ERROR(
                        f"[ALERT] {alert_type.upper()} DETECTED! Magnitude: {mag:.2f}g "
                        f"Location: {lat:.6f}, {lng:.6f}"
                    ))
                else:
                    mag = math.sqrt(acc_x**2 + acc_y**2 + acc_z**2)
                    self.stdout.write(
                        f"[OK] Sensor: acc={mag:.2f}g | "
                        f"GPS: {lat:.6f},{lng:.6f} | "
                        f"Speed: {speed:.0f}km/h"
                    )

                time.sleep(interval)

        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("\n\nSimulator stopped."))
