#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'park_management.settings')
django.setup()

from parking.models import User, ParkingSlot, Booking
from parking.serializers import BookingCreateSerializer
from datetime import datetime, date, time
import json

# Get a user
user = User.objects.first()
print(f"User: {user.username}, Role: {user.role}")

# Get an available slot
slot = ParkingSlot.objects.filter(status='Available').first()
print(f"Slot: {slot.slot_code if slot else 'None'}, Status: {slot.status if slot else 'N/A'}")

# Test data - match what frontend sends
booking_data = {
    'date': str(date.today()),
    'entry_time': '10:00',
    'exit_time': '12:00',
    'vehicle_type': 'Car',
    'slot_code': slot.slot_code if slot else 'F1A01',
    'car_number': user.car_number,
}

print("\n✓ Booking data to send:")
print(json.dumps(booking_data, indent=2))

# Test serializer
print("\n✓ Testing BookingCreateSerializer...")
serializer = BookingCreateSerializer(data=booking_data)
print(f"Serializer valid: {serializer.is_valid()}")

if not serializer.is_valid():
    print("❌ Validation errors:")
    print(json.dumps(serializer.errors, indent=2))
else:
    print("✓ All validations passed!")
    print("\nValidated data:")
    print(json.dumps(str(serializer.validated_data), indent=2))
