#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'park_management.settings')
django.setup()

from parking.models import User

# Update or create admin account
admin, created = User.objects.get_or_create(
    car_number='ADMIN-001',
    defaults={
        'username': 'admin',
        'email': 'admin@example.com',
        'role': 'Admin',
        'first_name': 'Admin',
        'last_name': 'User',
        'is_staff': True,
        'is_superuser': True
    }
)
admin.set_password('admin123')
admin.save()
print(f"✅ Admin: admin | Car: ADMIN-001 | Pass: admin123 | Role: Admin")

# Update/create staff account
staff, created = User.objects.get_or_create(
    car_number='STAFF-001',
    defaults={
        'username': 'STAFF-001',
        'email': 'staff@example.com',
        'role': 'Staff',
        'first_name': 'Staff',
        'last_name': 'Member'
    }
)
staff.set_password('staff123')
staff.save()
print(f"✅ Staff: STAFF-001 | Pass: staff123 | Role: Staff")

# Update/create test user
user, created = User.objects.get_or_create(
    car_number='DHA-1234',
    defaults={
        'username': 'DHA-1234',
        'email': 'user@example.com',
        'role': 'User',
        'first_name': 'John',
        'last_name': 'Doe'
    }
)
user.set_password('user123')
user.save()
print(f"✅ User: DHA-1234 | Pass: user123 | Role: User")
