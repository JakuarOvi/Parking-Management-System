#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'park_management.settings')
django.setup()

from parking.models import User, Booking, ParkingSlot
from django.db import connection

print("✅ Testing Database...")
with connection.cursor() as cursor:
    cursor.execute('SELECT VERSION()')
    version = cursor.fetchone()[0]
    print(f"MySQL Version: {version}")
    
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    print(f"Total Tables: {len(tables)}")

print(f"Users: {User.objects.count()}")
print(f"Slots: {ParkingSlot.objects.count()}")
print(f"Bookings: {Booking.objects.count()}")
print("✅ Database OK!")
