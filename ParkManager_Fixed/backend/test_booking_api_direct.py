#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'park_management.settings')
django.setup()

from rest_framework.test import APIClient
from parking.models import User, ParkingSlot

# Get a test user
user = User.objects.filter(role='User').first()
print(f"Testing with user: {user.username} ({user.car_number})")

# Create API client
client = APIClient()

# Force authenticate the client
client.force_authenticate(user=user)

# Prepare booking data
booking_data = {
    'slot_code': 'F1A01',
    'date': '2026-04-21',
    'entry_time': '10:00',
    'exit_time': '12:00',
    'vehicle_type': 'Car'
}

print(f"\n✓ Booking request data:")
print(json.dumps(booking_data, indent=2))

# Create booking via API
response = client.post('/api/bookings/', booking_data, format='json')

print(f"\n✓ Response status: {response.status_code}")

if response.status_code in [200, 201]:
    print("✓✓✓ BOOKING SUCCESSFUL! ✓✓✓")
    data = response.json()
    print(f"\n  Booking ID: {data.get('id')}")
    print(f"  Slot: {data.get('slot_code')}")
    print(f"  Entry: {data.get('entry_time')}")
    print(f"  Exit: {data.get('exit_time')}")
    print(f"  Total Charge: {data.get('total_charge')}")
    print(f"  Status: {data.get('status')}")
else:
    print(f"❌ ERROR!")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")
