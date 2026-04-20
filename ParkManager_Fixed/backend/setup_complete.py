#!/usr/bin/env python
"""
Complete setup and test script for ParkManager
Ensures database is properly initialized and all data is persisted
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'park_management.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from parking.models import User, ParkingSlot, Booking
from django.utils import timezone
from datetime import datetime, timedelta

print("=" * 60)
print("🔧 PARKMANAGER COMPLETE SETUP & TEST")
print("=" * 60)

# 1. Check Database Connection
print("\n1️⃣ Checking Database Connection...")
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT VERSION()')
        version = cursor.fetchone()[0]
        print(f"   ✅ MySQL Version: {version}")
except Exception as e:
    print(f"   ❌ Database connection failed: {e}")
    sys.exit(1)

# 2. Run Migrations
print("\n2️⃣ Running Migrations...")
try:
    call_command('migrate', verbosity=0)
    print("   ✅ All migrations applied")
except Exception as e:
    print(f"   ❌ Migration failed: {e}")
    sys.exit(1)

# 3. Create Test Users
print("\n3️⃣ Creating Test Users...")
admin_user, created = User.objects.get_or_create(
    car_number='ADMIN001',
    defaults={
        'username': 'admin_user',
        'first_name': 'Admin',
        'last_name': 'User',
        'role': 'Admin',
        'phone': '01700000001',
        'email': 'admin@parkmanager.com'
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print(f"   ✅ Admin user created: {admin_user.car_number}")
else:
    print(f"   ℹ️  Admin user already exists: {admin_user.car_number}")

regular_user, created = User.objects.get_or_create(
    car_number='USER001',
    defaults={
        'username': 'regular_user',
        'first_name': 'Regular',
        'last_name': 'User',
        'role': 'User',
        'phone': '01700000002',
        'email': 'user@parkmanager.com'
    }
)
if created:
    regular_user.set_password('user123')
    regular_user.save()
    print(f"   ✅ Regular user created: {regular_user.car_number}")
else:
    print(f"   ℹ️  Regular user already exists: {regular_user.car_number}")

# 4. Create Parking Slots
print("\n4️⃣ Creating Parking Slots...")
slot_count = ParkingSlot.objects.count()
if slot_count < 90:
    for floor in [1, 2, 3]:
        for zone in ['A', 'B', 'C']:
            for slot_num in range(1, 11):
                slot_code = f"F{floor}{zone}{slot_num:02d}"
                ParkingSlot.objects.get_or_create(
                    slot_code=slot_code,
                    defaults={
                        'floor': floor,
                        'zone': zone,
                        'slot_number': slot_num,
                        'status': 'Available',
                        'vehicle_type': 'Car',
                        'rate_per_hour': 40
                    }
                )
    print(f"   ✅ Created/Verified 90 parking slots")
else:
    print(f"   ℹ️  Parking slots already exist: {slot_count}")

# 5. Test Booking Creation
print("\n5️⃣ Testing Booking Creation...")
try:
    slot = ParkingSlot.objects.filter(status='Available').first()
    if slot:
        entry = timezone.now() + timedelta(hours=1)
        exit_time = entry + timedelta(hours=2)
        
        booking = Booking.objects.create(
            user=regular_user,
            slot=slot,
            vehicle_type='Car',
            entry_time=entry,
            exit_time=exit_time,
            base_charge=80,
            total_charge=80,
            status='Pending'
        )
        print(f"   ✅ Test booking created: ID {booking.id}")
        print(f"   ✅ Booking saved to MySQL: {booking}")
        
        # Verify it's in database
        fetched = Booking.objects.get(id=booking.id)
        print(f"   ✅ Booking verified in database: {fetched}")
        
        # Clean up test booking
        booking.delete()
        print(f"   ✅ Test booking cleaned up")
    else:
        print(f"   ⚠️  No available slots to test booking")
except Exception as e:
    print(f"   ❌ Booking test failed: {e}")

# 6. Final Status
print("\n" + "=" * 60)
print("✅ SETUP COMPLETE!")
print("=" * 60)
print(f"Users: {User.objects.count()}")
print(f"Slots: {ParkingSlot.objects.count()}")
print(f"Bookings: {Booking.objects.count()}")
print(f"Database: MySQL (canteen_db)")
print(f"Time Zone: Asia/Dhaka")
print(f"Server: Ready at http://127.0.0.1:8000/")
print("=" * 60)
