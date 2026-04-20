#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'park_management.settings')
django.setup()

from parking.models import User
from django.contrib.auth import authenticate

user = User.objects.filter(role='User').first()
print(f"User: {user.username}")
print(f"Car: {user.car_number}")

# Try to set password and test
user.set_password('user123')
user.save()
print("✓ Password set to 'user123'")

# Test login
auth_user = authenticate(username=user.username, password='user123')
if auth_user:
    print("✓ Login works!")
else:
    print("✗ Login failed")
