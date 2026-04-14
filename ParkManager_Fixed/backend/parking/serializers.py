from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import (User, ParkingSlot, Booking, Payment, Staff,
                     ShiftSchedule, Notification, Subscription, LostFound)
import qrcode
import io
from django.core.files.base import ContentFile
from datetime import datetime


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'car_number', 'name', 'role', 'phone', 'email',
                  'date_joined']
        read_only_fields = ['id', 'date_joined']

    def get_name(self, obj):
        return obj.name  # Uses the @property from User model


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4)
    name = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['car_number', 'name', 'password', 'phone', 'email']

    def create(self, validated_data):
        name = validated_data.pop('name', '')
        name_parts = name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        user = User.objects.create_user(
            username=validated_data.get('car_number'),
            car_number=validated_data.get('car_number'),
            password=validated_data.get('password'),
            email=validated_data.get('email', ''),
            phone=validated_data.get('phone', ''),
            first_name=first_name,
            last_name=last_name,
            role='User'  # Registration always creates User role
        )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=4)


class ParkingSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSlot
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    user_car_number = serializers.CharField(source='user.car_number', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    slot_code = serializers.CharField(source='slot.slot_code', read_only=True)
    hours_booked = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'qr_code', 'base_charge',
                            'overstay_charge', 'total_charge']

    def create(self, validated_data):
        from django.conf import settings
        user = validated_data['user']
        vehicle_type = validated_data['vehicle_type']
        entry_time = validated_data['entry_time']
        exit_time = validated_data['exit_time']
        booking_date = validated_data['date']

        rate = settings.PARKING_RATES.get(vehicle_type, 40)
        entry_dt = datetime.combine(booking_date, entry_time)
        exit_dt = datetime.combine(booking_date, exit_time)
        hours = max((exit_dt - entry_dt).total_seconds() / 3600, 0)
        base_charge = round(rate * hours, 2)

        validated_data['base_charge'] = base_charge
        validated_data['total_charge'] = base_charge

        booking = Booking.objects.create(**validated_data)

        # Generate QR code
        qr_data = f"BOOKING:{booking.id}|SLOT:{booking.slot.slot_code}|ENTRY:{booking.entry_time}|EXIT:{booking.exit_time}|CAR:{user.car_number}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        qr_img.save(buffer, format='PNG')
        booking.qr_code.save(f'qr_{booking.id}.png', ContentFile(buffer.getvalue()), save=True)

        return booking


class BookingCreateSerializer(serializers.ModelSerializer):
    car_number = serializers.CharField(write_only=True, required=False)
    mobile = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Booking
        fields = ['slot', 'date', 'entry_time', 'exit_time', 'vehicle_type', 'notes', 'car_number', 'mobile']


class PaymentSerializer(serializers.ModelSerializer):
    booking_detail = BookingSerializer(source='booking', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class StaffSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Staff
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        name = validated_data.pop('name', '')
        
        # Create user account
        employee_id = validated_data.get('employee_id')
        user = User.objects.create_user(
            username=employee_id,
            car_number=validated_data.get('user').car_number if 'user' in validated_data else employee_id,
            password=password or employee_id,  # Use employee_id as default password
            role='Staff'
        )
        
        if name:
            name_parts = name.split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            user.save()
        
        validated_data['user'] = user
        return super().create(validated_data)


class ShiftScheduleSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.user.name', read_only=True)
    staff_id_code = serializers.CharField(source='staff.staff_id', read_only=True)

    class Meta:
        model = ShiftSchedule
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['sent_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    user_car = serializers.CharField(source='user.car_number', read_only=True)

    class Meta:
        model = Subscription
        fields = '__all__'


class LostFoundSerializer(serializers.ModelSerializer):
    slot_code = serializers.CharField(source='slot.slot_code', read_only=True)
    found_by_name = serializers.CharField(source='found_by_staff.user.name', read_only=True)

    class Meta:
        model = LostFound
        fields = '__all__'


class DashboardStatsSerializer(serializers.Serializer):
    total_bookings = serializers.IntegerField()
    active_bookings = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2)
    member_tier = serializers.CharField()
    subscription_plan = serializers.CharField()
    unread_notifications = serializers.IntegerField()


class AdminDashboardSerializer(serializers.Serializer):
    active_bookings = serializers.IntegerField()
    today_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_slots = serializers.IntegerField()
    available_slots = serializers.IntegerField()
    occupied_slots = serializers.IntegerField()
    occupancy_rate = serializers.FloatField()
    overstay_count = serializers.IntegerField()
    today_bookings = serializers.IntegerField()
    monthly_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    staff_on_duty = serializers.IntegerField()
