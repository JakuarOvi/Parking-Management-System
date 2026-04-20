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
    subscription_plan = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'car_number', 'name', 'first_name', 'last_name', 'role', 'phone', 'email',
                  'profile_photo', 'subscription_plan', 'date_joined']
        read_only_fields = ['id', 'date_joined']

    def get_name(self, obj):
        return obj.name  # Uses the @property from User model

    def get_subscription_plan(self, obj):
        if hasattr(obj, 'subscription'):
            return obj.subscription.plan
        return 'None'


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


class BookingCreateSerializer(serializers.Serializer):
    slot_code = serializers.CharField(write_only=True, required=True)
    date = serializers.DateField(write_only=True, required=True)
    entry_time = serializers.TimeField(write_only=True, required=True)
    exit_time = serializers.TimeField(write_only=True, required=True)
    vehicle_type = serializers.CharField(write_only=True, required=True)
    notes = serializers.CharField(write_only=True, required=False, allow_blank=True)
    car_number = serializers.CharField(write_only=True, required=False)
    mobile = serializers.CharField(write_only=True, required=False)

    def validate_slot_code(self, value):
        try:
            slot = ParkingSlot.objects.get(slot_code=value)
            if slot.status in ['Maintenance', 'Disabled']:
                raise serializers.ValidationError("Slot is not available")
            return slot
        except ParkingSlot.DoesNotExist:
            raise serializers.ValidationError("Invalid slot code")

    def validate(self, data):
        from django.utils import timezone
        
        entry_time = data.get('entry_time')
        exit_time = data.get('exit_time')
        booking_date = data.get('date')
        slot = data.get('slot_code')
        vehicle_type = data.get('vehicle_type')
        
        if slot and vehicle_type and slot.vehicle_type != vehicle_type:
            raise serializers.ValidationError({"vehicle_type": "Vehicle type does not match slot type"})
        
        if entry_time and exit_time and entry_time >= exit_time:
            raise serializers.ValidationError({"exit_time": "Entry time must be before exit time"})
        
        if booking_date and booking_date < timezone.now().date():
            raise serializers.ValidationError({"date": "Booking date cannot be in the past"})
        
        # Convert time fields to datetime and make them aware
        if booking_date and entry_time:
            dt_entry = timezone.make_aware(datetime.combine(booking_date, entry_time))
            if dt_entry < timezone.now():
                raise serializers.ValidationError({"entry_time": "Booking time cannot be in the past"})
            data['entry_time'] = dt_entry
            
        if booking_date and exit_time:
            data['exit_time'] = timezone.make_aware(datetime.combine(booking_date, exit_time))
        
        return data

    def create(self, validated_data):
        from django.conf import settings
        
        slot = validated_data.pop('slot_code')
        vehicle_type = validated_data.pop('vehicle_type')
        entry_time = validated_data.pop('entry_time')
        exit_time = validated_data.pop('exit_time')
        validated_data.pop('date', None)  # Remove date as it's now in entry/exit times
        
        # Calculate charges
        rate = settings.PARKING_RATES.get(vehicle_type, 40)
        hours = max((exit_time - entry_time).total_seconds() / 3600, 0)
        base_charge = round(rate * hours, 2)
        
        # Create booking
        booking = Booking.objects.create(
            slot=slot,
            entry_time=entry_time,
            exit_time=exit_time,
            vehicle_type=vehicle_type,
            base_charge=base_charge,
            total_charge=base_charge,
            **validated_data
        )
        
        # Generate QR code
        try:
            qr_data = f"BOOKING:{booking.id}|SLOT:{slot.slot_code}|ENTRY:{booking.entry_time}|EXIT:{booking.exit_time}"
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            qr_img.save(buffer, format='PNG')
            booking.qr_code.save(f'qr_{booking.id}.png', ContentFile(buffer.getvalue()), save=True)
        except Exception as e:
            print(f"Warning: QR generation failed - {e}")  # QR generation is non-critical
        
        return booking


class PaymentSerializer(serializers.ModelSerializer):
    booking_detail = BookingSerializer(source='booking', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class StaffSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Staff
        fields = '__all__'


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
