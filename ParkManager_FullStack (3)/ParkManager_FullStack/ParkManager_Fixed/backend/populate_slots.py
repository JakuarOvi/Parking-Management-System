#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'park_management.settings')
django.setup()

from parking.models import ParkingSlot

# Create parking slots
created_count = 0
for floor in range(1, 4):  # 3 floors
    for zone in ['A', 'B', 'C']:  # 3 zones per floor
        for number in range(1, 11):  # 10 slots per zone
            slot_code = f'F{floor}{zone}{str(number).zfill(2)}'
            vehicle_type = {'A': 'Car', 'B': 'Bike', 'C': 'CNG'}[zone]
            rate = {'Car': 40, 'Bike': 20, 'CNG': 30}[vehicle_type]

            slot, created = ParkingSlot.objects.get_or_create(
                slot_code=slot_code,
                defaults={
                    'floor': floor,
                    'zone': zone,
                    'vehicle_type': vehicle_type,
                    'status': 'Available',
                    'is_reserved': False
                }
            )
            if created:
                created_count += 1

print(f"Created {created_count} parking slots")
print(f"Total slots: {ParkingSlot.objects.count()}")