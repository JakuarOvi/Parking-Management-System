#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'park_management.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

print("🔧 Fixing Database...")

# Get all tables from the database
with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"📋 Current tables: {len(tables)} found")
    print(f"   Tables: {tables}")

# Check if parking_booking table exists
with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES LIKE 'parking_booking'")
    if not cursor.fetchone():
        print("\n❌ parking_booking table missing!")
        print("🔄 Clearing migration history...")
        
        # Delete all migration records
        cursor.execute("DELETE FROM django_migrations")
        print(f"✅ Cleared migration history")
        
        connection.commit()

# Now run migrations
print("\n🚀 Running migrations...")
try:
    call_command('migrate', verbosity=2)
    print("✅ Migrations completed!")
except Exception as e:
    print(f"❌ Migration failed: {e}")

# Verify tables were created
print("\n✅ Verifying tables...")
with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"📋 Final tables: {len(tables)} found")
    
    # Check for parking tables
    for table in ['parking_booking', 'parking_slot', 'parking_user_profile', 'auth_user']:
        cursor.execute(f"SHOW TABLES LIKE '{table}'")
        if cursor.fetchone():
            print(f"   ✅ {table}")
        else:
            print(f"   ❌ {table}")

print("\n✅ Database fix completed!")
