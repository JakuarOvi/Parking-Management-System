#!/usr/bin/env python
"""
Complete database reset for ParkManager
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'park_management.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

print("=" * 70)
print("🚀 COMPLETE DATABASE RESET FOR PARKMANAGER")
print("=" * 70)

# Step 1: Drop ALL existing tables
print("\n📋 Step 1: Dropping all existing tables...")
with connection.cursor() as cursor:
    # Get all table names
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    
    if tables:
        print(f"   Found {len(tables)} tables to drop: {tables}")
        # Disable foreign key checks temporarily
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        
        # Drop all tables
        for table in tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
                print(f"   ✅ Dropped {table}")
            except Exception as e:
                print(f"   ⚠️  Could not drop {table}: {e}")
        
        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        connection.commit()
        print("✅ All tables dropped!")
    else:
        print("   No tables found")

# Step 2: Run fresh migrations
print("\n🔄 Step 2: Running fresh migrations...")
try:
    call_command('migrate', verbosity=2)
    print("✅ Migrations completed!")
except Exception as e:
    print(f"❌ Migration error: {e}")
    sys.exit(1)

# Step 3: Verify tables were created
print("\n✅ Step 3: Verifying database structure...")
with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"   Total tables: {len(tables)}")
    
    required_tables = [
        'auth_user',
        'parking_parkingslot', 
        'parking_booking',
        'django_migrations'
    ]
    
    for table in required_tables:
        if table in tables:
            print(f"   ✅ {table}")
        else:
            print(f"   ❌ {table} - MISSING!")

# Step 4: Create test data
print("\n👤 Step 4: Creating test users...")
from parking.models import User, ParkingSlot

# Create test users
users_data = [
    ('admin', 'admin@test.com', 'Admin', 'User', 'Admin', 'ADMIN-001'),
    ('staff_user', 'staff@test.com', 'Staff', 'User', 'Staff', 'STAFF-001'),
    ('regular_user', 'user@test.com', 'Regular', 'User', 'User', 'DHA-1234'),
]

for username, email, first_name, last_name, role, car_number in users_data:
    try:
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                first_name=first_name,
                last_name=last_name,
                role=role,
                car_number=car_number
            )
            print(f"   ✅ Created user: {username} (role: {role}, car: {car_number})")
        else:
            print(f"   ⚠️  User already exists: {username}")
    except Exception as e:
        print(f"   ❌ Could not create user {username}: {e}")

# Step 5: Create parking slots
print("\n🅿️  Step 5: Creating parking slots...")
try:
    floors = ['F1', 'F2', 'F3']
    zones = ['A', 'B', 'C']
    
    total_slots = 0
    for floor in floors:
        for zone in zones:
            for slot_num in range(1, 11):  # 10 slots per zone
                slot_code = f"{floor}{zone}{slot_num:02d}"
                
                try:
                    ParkingSlot.objects.get_or_create(
                        slot_code=slot_code,
                        defaults={
                            'floor': floor,
                            'zone': zone,
                            'is_available': True,
                            'vehicle_type': 'All'
                        }
                    )
                    total_slots += 1
                except Exception as e:
                    pass
    
    print(f"   ✅ Created {total_slots} parking slots")
except Exception as e:
    print(f"   ❌ Error creating parking slots: {e}")

# Final verification
print("\n" + "=" * 70)
print("✅ DATABASE RESET COMPLETE!")
print("=" * 70)
print("\n📊 Database Summary:")
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM auth_user")
    users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM parking_slot")
    slots = cursor.fetchone()[0]
    print(f"   ✅ Users: {users}")
    print(f"   ✅ Parking Slots: {slots}")

print("\n🚀 Ready to start the server!")
print("   Run: python manage.py runserver 8000")
print("=" * 70)
