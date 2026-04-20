from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ParkingSlot, Booking, Subscription, LostFound, Notification, Payment, Staff, ShiftSchedule


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('car_number', 'username', 'get_full_name', 'role', 'is_verified', 'created_at')
    list_filter = ('role', 'is_verified', 'created_at')
    search_fields = ('car_number', 'username', 'email')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Parking Info', {'fields': ('car_number', 'phone', 'role', 'is_verified')}),
    )


@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    list_display = ('slot_code', 'floor', 'vehicle_type', 'status', 'is_reserved')
    list_filter = ('floor', 'vehicle_type', 'status')
    search_fields = ('slot_code',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'slot', 'status', 'payment_status', 'entry_time', 'exit_time')
    list_filter = ('status', 'payment_status', 'vehicle_type', 'booking_date')
    search_fields = ('user__car_number', 'slot__slot_code')
    readonly_fields = ('created_at', 'booking_date')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date')
    list_filter = ('plan', 'status')
    search_fields = ('user__car_number',)


@admin.register(LostFound)
class LostFoundAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'floor', 'status', 'reported_date', 'reported_by')
    list_filter = ('status', 'floor', 'reported_date')
    search_fields = ('item_name', 'description')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'is_read', 'sent_at')
    list_filter = ('notification_type', 'is_read', 'sent_at')
    search_fields = ('title', 'message', 'user__car_number')
    readonly_fields = ('sent_at',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'booking__user__car_number')
    readonly_fields = ('created_at',)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'department', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('employee_id', 'user__username')


@admin.register(ShiftSchedule)
class ShiftScheduleAdmin(admin.ModelAdmin):
    list_display = ('staff', 'shift_type', 'date', 'assigned_floor', 'is_completed')
    list_filter = ('shift_type', 'date', 'is_completed')
    search_fields = ('staff__user__username',)

