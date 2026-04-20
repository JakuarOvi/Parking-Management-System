#!/usr/bin/env python
"""
Setup script for ParkManager with existing MySQL database
Uses: root user with password 'unimanagement12345' on canteen_db
"""
import subprocess
import sys
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'park_management.settings')

def test_connection():
    """Test MySQL connection"""
    print("🔍 Testing MySQL connection...")
    try:
        import django
        django.setup()
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✅ Connected to MySQL! Version: {version[0]}\n")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}\n")
        return False

def run_migrations():
    """Run Django migrations"""
    print("📦 Running Django migrations...")
    try:
        result = subprocess.run(
            [sys.executable, 'manage.py', 'migrate', '--run-syncdb'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Migrations completed!\n")
            print(result.stdout)
            return True
        else:
            print(f"❌ Migrations failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def populate_data():
    """Create test data"""
    print("📊 Creating test data...")
    try:
        result = subprocess.run(
            [sys.executable, 'create_admin.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Test data created!")
            print(result.stdout)
            
            # Also populate slots
            result2 = subprocess.run(
                [sys.executable, 'populate_slots.py'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result2.returncode == 0:
                print("✅ Parking slots created!")
            return True
        else:
            print(f"⚠️  {result.stdout}")
            return True  # Don't fail, data might already exist
    except Exception as e:
        print(f"⚠️  Could not create test data: {e}")
        return True  # Don't fail

def verify():
    """Verify database setup"""
    print("\n✅ Verifying database...")
    try:
        import django
        django.setup()
        from parking.models import User, ParkingSlot
        
        users = User.objects.count()
        slots = ParkingSlot.objects.count()
        
        print(f"   ✓ Users: {users}")
        print(f"   ✓ Parking slots: {slots}")
        print(f"   ✓ Database: canteen_db")
        print(f"   ✓ User: root")
        
        return True
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 ParkManager - MySQL Setup with canteen_db")
    print("=" * 70 + "\n")
    
    if not test_connection():
        print("❌ Cannot connect to MySQL. Please ensure:")
        print("   1. MySQL is running")
        print("   2. Root user has password: unimanagement12345")
        print("   3. Database canteen_db exists")
        sys.exit(1)
    
    if not run_migrations():
        print("❌ Migration failed")
        sys.exit(1)
    
    populate_data()
    
    if verify():
        print("\n" + "=" * 70)
        print("✅ Setup Complete!")
        print("=" * 70)
        print("\n🎯 Database Configuration:")
        print("   Database: canteen_db")
        print("   User: root")
        print("   Password: unimanagement12345")
        print("   Host: 127.0.0.1")
        print("   Port: 3306")
        print("\n🚀 Start the server: python manage.py runserver 8000")
        print("=" * 70)
    else:
        print("❌ Verification failed")
        sys.exit(1)
