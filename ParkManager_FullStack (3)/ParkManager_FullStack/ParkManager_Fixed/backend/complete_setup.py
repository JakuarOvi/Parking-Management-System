#!/usr/bin/env python
"""
Complete MySQL Setup and Migration Script for ParkManager
"""
import subprocess
import sys
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'park_management.settings')

def test_mysql_connection():
    """Test MySQL connection"""
    print("\n🔍 Testing MySQL connection...")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✅ MySQL connected! Version: {version[0]}")
            return True
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        return False

def setup_mysql_database():
    """Set up MySQL database"""
    print("\n🔧 Setting up MySQL database...")
    
    # Try using Django's built-in migration system which handles db creation better
    try:
        django.setup()
        from django.core.management import call_command
        
        # Run migrations
        print("📦 Running Django migrations...")
        call_command('migrate', verbosity=2)
        print("✅ Migrations completed successfully!")
        return True
    except Exception as e:
        error_msg = str(e)
        if "Unknown database" in error_msg:
            print(f"❌ Database 'parkmanagement' does not exist.")
            print("\n📝 Please run these commands in your MySQL terminal:")
            print("=" * 70)
            print("mysql -u root -p")
            print("(enter your MySQL root password)")
            print("\nThen execute:")
            print("-" * 70)
            print("CREATE DATABASE parkmanagement;")
            print("CREATE USER 'parkuser'@'127.0.0.1' IDENTIFIED BY 'parkpass123';")
            print("CREATE USER 'parkuser'@'localhost' IDENTIFIED BY 'parkpass123';")
            print("GRANT ALL PRIVILEGES ON parkmanagement.* TO 'parkuser'@'127.0.0.1';")
            print("GRANT ALL PRIVILEGES ON parkmanagement.* TO 'parkuser'@'localhost';")
            print("FLUSH PRIVILEGES;")
            print("EXIT;")
            print("=" * 70)
            return False
        else:
            print(f"❌ Migration error: {error_msg}")
            return False

def populate_test_data():
    """Populate test data"""
    print("\n📊 Populating test data...")
    try:
        from django.core.management import call_command
        from parking.models import User, ParkingSlot
        
        # Create admin user if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@parkmanagement.com',
                password='admin123',
                car_number='ADMIN-001',
                role='Admin'
            )
            print("✅ Admin user created")
        
        # Create parking slots if not exists
        if ParkingSlot.objects.count() == 0:
            slots = []
            for floor in [1, 2, 3]:
                for zone in ['A', 'B', 'C']:
                    for slot_num in range(1, 11):
                        slot_code = f"F{floor}{zone}{slot_num:02d}"
                        vehicle_type = 'Car'
                        slots.append(ParkingSlot(
                            slot_code=slot_code,
                            floor=floor,
                            zone=zone,
                            status='Available',
                            vehicle_type=vehicle_type
                        ))
            
            ParkingSlot.objects.bulk_create(slots)
            print(f"✅ Created {len(slots)} parking slots")
        
        return True
    except Exception as e:
        print(f"⚠️  Could not populate test data: {e}")
        return False

def verify_setup():
    """Verify complete setup"""
    print("\n✅ Verifying setup...")
    try:
        django.setup()
        from django.db import connection
        from parking.models import User, ParkingSlot
        
        # Check connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM auth_user")
            user_count = cursor.fetchone()[0]
        
        slot_count = ParkingSlot.objects.count()
        
        print(f"   - Users in database: {user_count}")
        print(f"   - Parking slots in database: {slot_count}")
        print("\n✅ Setup verification complete!")
        return True
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 ParkManager MySQL Setup & Migration")
    print("=" * 70)
    
    # Step 1: Test connection
    if not test_mysql_connection():
        print("\n⚠️  Could not connect to MySQL. You may need to:")
        print("   1. Ensure MySQL service is running")
        print("   2. Check MySQL credentials in settings.py")
        print("   3. Create the 'parkmanagement' database manually")
        sys.exit(1)
    
    # Step 2: Run migrations
    if not setup_mysql_database():
        print("\n⚠️  Database setup incomplete. Please follow the instructions above.")
        sys.exit(1)
    
    # Step 3: Populate test data
    populate_test_data()
    
    # Step 4: Verify
    verify_setup()
    
    print("\n" + "=" * 70)
    print("✅ MySQL setup completed successfully!")
    print("   Your application is now using MySQL for persistent storage.")
    print("=" * 70)
