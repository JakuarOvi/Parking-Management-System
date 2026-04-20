#!/usr/bin/env python
import os
import django
import json
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'park_management.settings')
django.setup()

from parking.models import User
from django.contrib.auth import authenticate

# Get a user to login with
user = User.objects.filter(role='User').first()
if not user:
    print("No user found to test with")
    exit(1)

print(f"Testing with user: {user.username} (car: {user.car_number})")

# Login first
login_data = {
    'car_number': user.car_number,
    'password': 'user123',
    'role': 'User'
}

session = requests.Session()
login_response = session.post('http://127.0.0.1:8000/api/auth/login/', json=login_data)
print(f"\n✓ Login response: {login_response.status_code}")
if login_response.status_code != 200:
    print(f"  Error: {login_response.text}")
else:
    print(f"  Success! Logged in as {login_response.json()['user']['car_number']}")

# Now try to create a booking
booking_data = {
    'slot_code': 'F1A01',
    'date': '2026-04-21',
    'entry_time': '10:00',
    'exit_time': '12:00',
    'vehicle_type': 'Car'
}

print(f"\n✓ Booking request data:")
print(json.dumps(booking_data, indent=2))

booking_response = session.post('http://127.0.0.1:8000/api/bookings/', json=booking_data)
print(f"\n✓ Booking response: {booking_response.status_code}")

if booking_response.status_code in [200, 201]:
    print("✓ BOOKING SUCCESSFUL!")
    result = booking_response.json()
    print(f"  Booking ID: {result.get('id')}")
    print(f"  Slot: {result.get('slot_code')}")
    print(f"  Entry: {result.get('entry_time')}")
    print(f"  Exit: {result.get('exit_time')}")
else:
    print(f"❌ BOOKING FAILED!")
    print(f"  Error: {booking_response.text}")
