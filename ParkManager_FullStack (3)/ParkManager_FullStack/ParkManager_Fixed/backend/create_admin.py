#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'park_management.settings')
django.setup()

from parking.models import User

# Create admin user
try:
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        car_number='ADMIN-001',
        role='Admin'
    )
    print(f"✅ Admin account created successfully!")
    print(f"Username: admin")
    print(f"Password: admin123")
    print(f"Car Number: ADMIN-001")
    print(f"Role: Admin")
except Exception as e:
    print(f"Admin account might already exist or error: {e}")
    
# Also create a staff user for testing
try:
    staff = User.objects.create_user(
        username='STAFF-001',
        password='staff123',
        email='staff@example.com',
        car_number='STAFF-001',
        role='Staff',
        first_name='Staff',
        last_name='Member'
    )
    print(f"\n✅ Staff account created!")
    print(f"Username/Car: STAFF-001")
    print(f"Password: staff123")
    print(f"Role: Staff")
except Exception as e:
    print(f"Staff account creation error: {e}")

# Create a test user
try:
    user = User.objects.create_user(
        username='DHA-1234',
        password='user123',
        email='user@example.com',
        car_number='DHA-1234',
        role='User',
        first_name='John',
        last_name='Doe'
    )
    print(f"\n✅ Test User account created!")
    print(f"Username/Car: DHA-1234")
    print(f"Password: user123")
    print(f"Role: User")
except Exception as e:
    print(f"User account creation error: {e}")
