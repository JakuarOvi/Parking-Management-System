#!/usr/bin/env python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'park_management.settings')
import django
django.setup()

from parking.models import User
from django.contrib.auth import authenticate

admin = User.objects.get(car_number='ADMIN-001')
print(f"Username: {admin.username}")
print(f"Car Number: {admin.car_number}")
print(f"Password Hash Set: {bool(admin.password)}")
print(f"Password Check: {admin.check_password('admin123')}")
print(f"Is Staff: {admin.is_staff}")
print(f"Is Superuser: {admin.is_superuser}")
print(f"Role: {admin.role}")

# Test authenticate function
auth_user = authenticate(username='ADMIN-001', password='admin123')
print(f"\nAuthenticate Result: {auth_user}")

# Try with username field
auth_user2 = authenticate(username='admin', password='admin123')
print(f"Authenticate with admin: {auth_user2}")
