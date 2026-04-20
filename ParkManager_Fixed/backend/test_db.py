import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'park_management.settings')
django.setup()

from django.db import connection
from parking.models import User, ParkingSlot, Booking

print('🔍 DATABASE CONNECTION TEST:')
with connection.cursor() as cursor:
    cursor.execute('SELECT VERSION()')
    version = cursor.fetchone()[0]
    print(f'✅ MySQL Version: {version}')

print('\n📊 TABLE COUNTS:')
print(f'   Users: {User.objects.count()}')
print(f'   Parking Slots: {ParkingSlot.objects.count()}')
print(f'   Bookings: {Booking.objects.count()}')

if User.objects.count() > 0:
    user = User.objects.first()
    print(f'\n👤 Sample User: {user.username} (Role: {user.role})')
else:
    print('\n⚠️  No users created yet')
    
print('\n✅ Database connection successful!')
