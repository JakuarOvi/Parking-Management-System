from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Custom User model for parking system."""
    ROLE_CHOICES = [
        ('User', 'Regular User'),
        ('Staff', 'Parking Staff'),
        ('Admin', 'Administrator'),
    ]
    
    car_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        validators=[RegexValidator(r'^[A-Z]{2,3}-\d{4}$', 'Invalid car number format')]
    )
    phone = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='User')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.car_number or self.username} ({self.role})"
    
    @property
    def name(self):
        """Return full name or username."""
        full_name = self.get_full_name().strip()
        return full_name if full_name else self.username


class ParkingSlot(models.Model):
    """Parking slot model."""
    FLOOR_CHOICES = [(i, f'Floor {i}') for i in range(1, 6)]
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Occupied', 'Occupied'),
        ('Maintenance', 'Maintenance'),
    ]
    VEHICLE_TYPE_CHOICES = [
        ('Car', 'Car'),
        ('Bike', 'Bike'),
        ('CNG', 'CNG'),
    ]

    slot_code = models.CharField(max_length=10, unique=True)
    floor = models.IntegerField(choices=FLOOR_CHOICES)
    zone = models.CharField(max_length=1, default='A')  # A, B, C
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPE_CHOICES)
    is_reserved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'parking_slot'

    def __str__(self):
        return f"{self.slot_code} - {self.status}"


class Booking(models.Model):
    """Parking booking model."""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    slot = models.ForeignKey(ParkingSlot, on_delete=models.SET_NULL, null=True, related_name='bookings')
    vehicle_type = models.CharField(max_length=10, choices=ParkingSlot.VEHICLE_TYPE_CHOICES)
    entry_time = models.DateTimeField()
    exit_time = models.DateTimeField(null=True, blank=True)
    actual_entry = models.DateTimeField(null=True, blank=True)
    actual_exit = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    base_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overstay_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Unpaid')
    booking_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)
    qr_code = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'booking'

    def __str__(self):
        return f"Booking #{self.id} - {self.user.car_number}"


class Subscription(models.Model):
    """User subscription plan model."""
    PLAN_CHOICES = [
        ('Basic', 'Basic - 500/month'),
        ('Gold', 'Gold - 800/month'),
        ('Premium', 'Premium - 1200/month'),
    ]
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Expired', 'Expired'),
        ('Pending', 'Pending'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subscription'

    def __str__(self):
        return f"{self.user.car_number} - {self.plan}"


class Notification(models.Model):
    """User notification model."""
    TYPE_CHOICES = [
        ('Booking', 'Booking'),
        ('Overstay', 'Overstay'),
        ('Payment', 'Payment'),
        ('System', 'System'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification'
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.title} - {self.user.car_number}"


class Payment(models.Model):
    """Payment model."""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=50, default='Cash')
    transaction_id = models.CharField(max_length=255, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment'

    def __str__(self):
        return f"Payment {self.id} - {self.amount}"


class Staff(models.Model):
    """Staff member model."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100, default='Parking Management')
    is_active = models.BooleanField(default=True)
    is_on_duty = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'staff'

    def __str__(self):
        return f"Staff - {self.user.username}"


class ShiftSchedule(models.Model):
    """Shift schedule model."""
    SHIFT_CHOICES = [
        ('Morning', 'Morning (6AM - 2PM)'),
        ('Evening', 'Evening (2PM - 10PM)'),
        ('Night', 'Night (10PM - 6AM)'),
    ]

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='shifts')
    shift_type = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    assigned_floor = models.IntegerField(null=True, blank=True)
    date = models.DateField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shift_schedule'

    def __str__(self):
        return f"{self.staff.user.username} - {self.shift_type} on {self.date}"


class LostFound(models.Model):
    """Lost and found items model."""
    STATUS_CHOICES = [
        ('Reported', 'Reported'),
        ('Found', 'Found'),
        ('Claimed', 'Claimed'),
    ]

    item_name = models.CharField(max_length=255)
    description = models.TextField()
    floor = models.IntegerField()
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='lost_items_reported')
    found_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='items_found')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Reported')
    claimed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='items_claimed')
    reported_date = models.DateTimeField(auto_now_add=True)
    found_date = models.DateTimeField(null=True, blank=True)
    claimed_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'lost_found'

    def __str__(self):
        return f"{self.item_name} - {self.status}"
