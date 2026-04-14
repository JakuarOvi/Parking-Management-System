from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
# from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum, Count, Q
from django.db import transaction
import calendar
from datetime import datetime, date, timedelta
from decimal import Decimal
import csv
import io
from django.http import HttpResponse

from .models import (User, ParkingSlot, Booking, Payment, Staff,
                     ShiftSchedule, Notification, Subscription, LostFound)
from .serializers import *
from .permissions import IsAdminOrStaff, IsAdmin


# ─── AUTH ────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    car_number = request.data.get('car_number', '').upper()
    password = request.data.get('password', '')
    role = request.data.get('role', 'User')

    # First, find user by car_number
    try:
        user = User.objects.get(car_number=car_number)
    except User.DoesNotExist:
        return Response({'error': 'Wrong username or password'}, status=401)
    
    # Check password
    if not user.check_password(password):
        return Response({'error': 'Wrong username or password'}, status=401)
    
    # Check role
    if user.role != role:
        return Response({'error': f'This account is not a {role} account'}, status=403)

    # refresh = RefreshToken.for_user(user)
    return Response({
        'message': 'Login successful',
        'user': UserSerializer(user).data,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # refresh = RefreshToken.for_user(user)
        return Response({'message': 'Registration successful',
                         'user': UserSerializer(user).data}, status=201)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    # try:
    #     refresh_token = request.data['refresh']
    #     token = RefreshToken(refresh_token)
    #     token.blacklist()
    # except Exception:
    #     pass
    return Response({'message': 'Logged out successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    if not request.user.check_password(serializer.validated_data['old_password']):
        return Response({'error': 'Wrong password'}, status=400)
    request.user.set_password(serializer.validated_data['new_password'])
    request.user.save()
    return Response({'message': 'Password changed'})


# ─── USER DASHBOARD ──────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard(request):
    user = request.user
    bookings = user.bookings.all()
    payments = Payment.objects.filter(booking__user=user, status='Completed')
    total_spent = payments.aggregate(total=Sum('amount'))['total'] or 0
    data = {
        'total_bookings': bookings.count(),
        'active_bookings': bookings.filter(status__in=['Active', 'Pending']).count(),
        'total_spent': total_spent,
        'member_tier': user.member_tier,
        'subscription_plan': user.subscription_plan,
        'unread_notifications': user.notifications.filter(is_read=False).count(),
    }
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_profile(request):
    return Response(UserSerializer(request.user).data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


# ─── SLOTS ───────────────────────────────────────────────────────────────────

class ParkingSlotViewSet(viewsets.ModelViewSet):
    queryset = ParkingSlot.objects.all()
    serializer_class = ParkingSlotSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = ParkingSlot.objects.all()
        floor = self.request.query_params.get('floor')
        zone = self.request.query_params.get('zone')
        vehicle_type = self.request.query_params.get('vehicle_type')
        status = self.request.query_params.get('status')
        if floor: qs = qs.filter(floor=floor)
        if zone: qs = qs.filter(zone=zone)
        if vehicle_type: qs = qs.filter(vehicle_type=vehicle_type)
        if status: qs = qs.filter(status=status)
        return qs


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def slot_blueprint(request):
    floors = {}
    for floor_num in [1, 2, 3]:
        floors[f'floor_{floor_num}'] = {}
        for zone in ['A', 'B', 'C']:
            slots = ParkingSlot.objects.filter(floor=floor_num, zone=zone)
            floors[f'floor_{floor_num}'][f'zone_{zone}'] = ParkingSlotSerializer(slots, many=True).data
    return Response(floors)


# ─── BOOKINGS ────────────────────────────────────────────────────────────────

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'Admin':
            qs = Booking.objects.all().select_related('user', 'slot')
        elif user.role == 'Staff':
            qs = Booking.objects.filter(date=date.today()).select_related('user', 'slot')
        else:
            qs = Booking.objects.filter(user=user).select_related('slot')

        status_filter = self.request.query_params.get('status')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if status_filter: qs = qs.filter(status=status_filter)
        if date_from: qs = qs.filter(date__gte=date_from)
        if date_to: qs = qs.filter(date__lte=date_to)
        return qs.order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = BookingCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        booking_date = serializer.validated_data['date']
        entry_time = serializer.validated_data['entry_time']
        exit_time = serializer.validated_data['exit_time']
        slot = serializer.validated_data['slot']

        if booking_date < date.today():
            return Response({'error': 'Booking date cannot be in the past'}, status=400)
        if entry_time >= exit_time:
            return Response({'error': 'Entry time must be before exit time'}, status=400)
        if slot.status == 'Disabled':
            return Response({'error': 'Slot is disabled'}, status=400)

        # Check for conflicting bookings
        conflicts = Booking.objects.filter(
            slot=slot,
            date=booking_date,
            status__in=['Pending', 'Active'],
        ).filter(
            Q(entry_time__lt=exit_time) &
            Q(exit_time__gt=entry_time)
        )
        if conflicts.exists():
            return Response({'error': 'Slot already booked for this time'}, status=400)

        # Handle user assignment
        user = request.user
        if request.user.role == 'Admin' and 'car_number' in serializer.validated_data:
            car_number = serializer.validated_data['car_number'].upper()
            mobile = serializer.validated_data.get('mobile', '')
            
            # Try to get existing user or create new one
            try:
                user = User.objects.get(car_number=car_number)
            except User.DoesNotExist:
                # Create new user account
                user = User.objects.create_user(
                    username=car_number,
                    car_number=car_number,
                    password=mobile,
                    role='User'
                )

        full_data = dict(serializer.validated_data)
        full_data['user'] = user
        # Remove car_number and mobile from validated data as they're not part of Booking model
        full_data.pop('car_number', None)
        full_data.pop('mobile', None)
        
        booking_serializer = BookingSerializer(data=full_data)
        booking_serializer.is_valid(raise_exception=True)
        booking = booking_serializer.save()

        Notification.objects.create(
            user=user,
            notification_type='Booking',
            title='Booking Confirmed',
            message=f'Your booking for slot {slot.slot_code} has been confirmed. Booking ID: {str(booking.id)[:8]}'
        )

        return Response(BookingSerializer(booking).data, status=201)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status not in ['Pending', 'Active']:
            return Response({'error': 'Cannot cancel this booking'}, status=400)
        if booking.user != request.user and request.user.role not in ['Admin', 'Staff']:
            return Response({'error': 'Permission denied'}, status=403)
        booking.status = 'Cancelled'
        if booking.slot.status == 'Occupied':
            booking.slot.status = 'Available'
            booking.slot.save()
        booking.save()
        return Response({'message': 'Booking cancelled'})

    @action(detail=True, methods=['post'])
    def scan_entry(self, request, pk=None):
        if request.user.role not in ['Admin', 'Staff']:
            return Response({'error': 'Staff only'}, status=403)
        booking = self.get_object()
        if booking.status != 'Pending':
            return Response({'error': f'Invalid booking status: {booking.status}'}, status=400)
        booking.status = 'Active'
        booking.actual_entry = timezone.now()
        booking.slot.status = 'Occupied'
        booking.slot.save()
        booking.save()
        # Broadcast via WebSocket
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'parking_slots',
            {'type': 'slot_update', 'slot_id': booking.slot.id,
             'status': 'Occupied', 'slot_code': booking.slot.slot_code}
        )
        return Response({'message': 'Entry logged', 'actual_entry': booking.actual_entry})

    @action(detail=True, methods=['post'])
    def scan_exit(self, request, pk=None):
        if request.user.role not in ['Admin', 'Staff']:
            return Response({'error': 'Staff only'}, status=403)
        booking = self.get_object()
        if booking.status not in ['Active', 'Overstay']:
            return Response({'error': f'Cannot exit from status: {booking.status}'}, status=400)
        booking.actual_exit = timezone.now()
        booking.status = 'Completed'
        booking.slot.status = 'Available'
        booking.slot.save()

        # Calculate overstay
        planned_exit = datetime.combine(booking.booking_date, booking.exit_time)
        planned_exit = timezone.make_aware(planned_exit)
        if booking.actual_exit > planned_exit:
            overstay_hours = (booking.actual_exit - planned_exit).total_seconds() / 3600
            booking.overstay_charge = round(overstay_hours * settings.OVERSTAY_PENALTY_RATE, 2)
            booking.total_charge = booking.base_charge + booking.overstay_charge
        booking.save()

        # Broadcast via WebSocket
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'parking_slots',
            {'type': 'slot_update', 'slot_id': booking.slot.id,
             'status': 'Available', 'slot_code': booking.slot.slot_code}
        )
        return Response({'message': 'Exit logged', 'total_charge': booking.total_charge,
                         'overstay_charge': booking.overstay_charge})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def scan_qr(request):
    """Staff scans QR code to get booking info"""
    if request.user.role not in ['Admin', 'Staff']:
        return Response({'error': 'Staff only'}, status=403)
    booking_id = request.data.get('booking_id')
    try:
        booking = Booking.objects.get(id=booking_id)
        return Response(BookingSerializer(booking).data)
    except Booking.DoesNotExist:
        return Response({'error': 'Invalid QR code'}, status=404)


# ─── PAYMENTS ────────────────────────────────────────────────────────────────

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'Admin':
            return Payment.objects.all().select_related('booking__user', 'booking__slot')
        elif user.role == 'Staff':
            return Payment.objects.filter(booking__date=date.today())
        return Payment.objects.filter(booking__user=user)

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        if request.user.role not in ['Admin', 'Staff']:
            return Response({'error': 'Staff only'}, status=403)
        payment = self.get_object()
        payment.status = 'Completed'
        payment.payment_method = request.data.get('payment_method', 'Cash')
        payment.transaction_id = request.data.get('transaction_id', '')
        payment.paid_at = timezone.now()
        payment.save()
        payment.booking.status = 'Completed'
        payment.booking.save()
        # Generate PDF receipt
        from .utils import generate_receipt_pdf
        generate_receipt_pdf(payment)
        return Response({'message': 'Payment marked', 'payment': PaymentSerializer(payment).data})

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        if request.user.role != 'Admin':
            return Response({'error': 'Admin only'}, status=403)
        payment = self.get_object()
        payment.status = 'Refunded'
        payment.refund_amount = request.data.get('refund_amount', payment.amount)
        payment.refund_reason = request.data.get('reason', '')
        payment.save()
        return Response({'message': 'Refund processed'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
    booking_id = request.data.get('booking_id')
    method = request.data.get('method', 'Cash')
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=404)

    if hasattr(booking, 'payment'):
        return Response({'error': 'Payment already exists'}, status=400)

    payment = Payment.objects.create(
        booking=booking,
        amount=booking.total_charge,
        method=method,
        status='Pending',
    )
    return Response(PaymentSerializer(payment).data, status=201)


# ─── ADMIN ───────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):
    if request.user.role != 'Admin':
        return Response({'error': 'Admin only'}, status=403)
    today = date.today()
    today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    today_end = timezone.make_aware(datetime.combine(today, datetime.max.time()))
    month_start = today.replace(day=1)

    active = Booking.objects.filter(status__in=['Active', 'Pending']).count()
    today_income = Payment.objects.filter(status='Completed', paid_at__range=[today_start, today_end]).aggregate(t=Sum('amount'))['t'] or 0
    monthly_income = Payment.objects.filter(status='Completed', paid_at__date__gte=month_start).aggregate(t=Sum('amount'))['t'] or 0
    total_slots = ParkingSlot.objects.count()
    available = ParkingSlot.objects.filter(status='Available').count()
    occupied = ParkingSlot.objects.filter(status='Occupied').count()
    occupancy_rate = round((occupied / total_slots * 100) if total_slots else 0, 1)
    overstay = Booking.objects.filter(status='Overstay').count()
    today_bookings = Booking.objects.filter(date=today).count()
    staff_on = Staff.objects.filter(is_on_duty=True).count()

    return Response({
        'active_bookings': active,
        'today_income': today_income,
        'monthly_income': monthly_income,
        'total_slots': total_slots,
        'available_slots': available,
        'occupied_slots': occupied,
        'occupancy_rate': occupancy_rate,
        'overstay_count': overstay,
        'today_bookings': today_bookings,
        'staff_on_duty': staff_on,
    })


# ─── STAFF ───────────────────────────────────────────────────────────────────

class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all().select_related('user')
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = StaffSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        # Create user account for staff
        employee_id = request.data.get('employee_id')
        car_number = request.data.get('car_number', employee_id)
        password = request.data.get('password', employee_id)  # Default password is employee_id
        name = request.data.get('name', '')
        
        # Create user
        user = User.objects.create_user(
            username=employee_id,
            car_number=car_number,
            password=password,
            role='Staff'
        )
        
        if name:
            name_parts = name.split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            user.save()
        
        # Add user to validated data
        validated_data = serializer.validated_data.copy()
        validated_data['user'] = user
        
        staff = Staff.objects.create(**validated_data)
        return Response(StaffSerializer(staff).data, status=201)

    @action(detail=True, methods=['post'])
    def toggle_duty(self, request, pk=None):
        staff = self.get_object()
        if request.user.role not in ['Admin', 'Staff'] and request.user != staff.user:
            return Response({'error': 'Permission denied'}, status=403)
        staff.is_on_duty = not staff.is_on_duty
        staff.save()
        return Response({'is_on_duty': staff.is_on_duty})


class ShiftScheduleViewSet(viewsets.ModelViewSet):
    queryset = ShiftSchedule.objects.all().select_related('staff__user')
    serializer_class = ShiftScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == 'Staff':
            try:
                staff = self.request.user.staff_profile
                qs = qs.filter(staff=staff)
            except Staff.DoesNotExist:
                return qs.none()
        return qs


# ─── NOTIFICATIONS ───────────────────────────────────────────────────────────

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'Admin':
            return Notification.objects.all().order_by('-sent_at')
        return Notification.objects.filter(user=user).order_by('-sent_at')

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return Response({'message': 'All marked as read'})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save()
        return Response({'message': 'Marked as read'})

    @action(detail=False, methods=['post'])
    def broadcast(self, request):
        if request.user.role != 'Admin':
            return Response({'error': 'Admin only'}, status=403)
        message = request.data.get('message', '')
        title = request.data.get('title', 'Notification')
        users = User.objects.filter(role='User', is_active=True)
        notifications = [Notification(user=u, type='General', title=title, message=message) for u in users]
        Notification.objects.bulk_create(notifications)
        return Response({'message': f'Broadcast sent to {len(notifications)} users'})


# ─── SUBSCRIPTIONS ────────────────────────────────────────────────────────────

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all().select_related('user')
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'Admin':
            return Subscription.objects.all()
        return Subscription.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        plan = request.data.get('plan')
        plan_prices = settings.SUBSCRIPTION_PLANS
        if plan not in plan_prices:
            return Response({'error': 'Invalid plan'}, status=400)
        start = date.today()
        if start.month == 12:
            year = start.year + 1
            month = 1
        else:
            year = start.year
            month = start.month + 1
        end_day = min(start.day, calendar.monthrange(year, month)[1])
        end = date(year, month, end_day)

        sub = Subscription.objects.create(
            user=request.user, plan=plan,
            start_date=start, end_date=end,
            amount_paid=plan_prices[plan], is_active=True
        )
        request.user.subscription_plan = plan
        request.user.save()
        return Response(SubscriptionSerializer(sub).data, status=201)


# ─── LOST & FOUND ─────────────────────────────────────────────────────────────

class LostFoundViewSet(viewsets.ModelViewSet):
    queryset = LostFound.objects.all().select_related('slot', 'found_by_staff__user')
    serializer_class = LostFoundSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def mark_claimed(self, request, pk=None):
        if request.user.role not in ['Admin', 'Staff']:
            return Response({'error': 'Staff only'}, status=403)
        item = self.get_object()
        item.status = 'Claimed'
        item.claimed_at = timezone.now()
        item.save()
        return Response({'message': 'Item marked as claimed'})


# ─── REPORTS ─────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reports_data(request):
    if request.user.role != 'Admin':
        return Response({'error': 'Admin only'}, status=403)
    period = request.query_params.get('period', 'weekly')
    today = date.today()

    if period == 'daily':
        start = today - timedelta(days=30)
        bookings = Booking.objects.filter(date__gte=start)
        daily = bookings.values('date').annotate(
            count=Count('id'),
            income=Sum('total_charge')
        ).order_by('date')
        labels = [str(d['date']) for d in daily]
        income_data = [float(d['income'] or 0) for d in daily]
        count_data = [d['count'] for d in daily]
    elif period == 'monthly':
        start = today - timedelta(days=365)
        bookings = Booking.objects.filter(date__gte=start)
        from django.db.models.functions import TruncMonth
        monthly = bookings.annotate(month=TruncMonth('date')).values('month').annotate(
            count=Count('id'), income=Sum('total_charge')
        ).order_by('month')
        labels = [d['month'].strftime('%b %Y') for d in monthly]
        income_data = [float(d['income'] or 0) for d in monthly]
        count_data = [d['count'] for d in monthly]
    else:  # weekly
        start = today - timedelta(weeks=12)
        bookings = Booking.objects.filter(date__gte=start)
        from django.db.models.functions import TruncWeek
        weekly = bookings.annotate(week=TruncWeek('date')).values('week').annotate(
            count=Count('id'), income=Sum('total_charge')
        ).order_by('week')
        labels = [d['week'].strftime('W%U %Y') for d in weekly]
        income_data = [float(d['income'] or 0) for d in weekly]
        count_data = [d['count'] for d in weekly]

    vehicle_breakdown = Booking.objects.values('vehicle_type').annotate(count=Count('id'))
    slot_occupancy = ParkingSlot.objects.values('status').annotate(count=Count('id'))

    return Response({
        'labels': labels,
        'income_data': income_data,
        'count_data': count_data,
        'vehicle_breakdown': list(vehicle_breakdown),
        'slot_occupancy': list(slot_occupancy),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_csv(request):
    if request.user.role != 'Admin':
        return Response({'error': 'Admin only'}, status=403)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bookings_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Car Number', 'Slot', 'Date', 'Entry', 'Exit',
                     'Vehicle', 'Hours', 'Base Charge', 'Overstay', 'Total', 'Status'])
    for b in Booking.objects.all().select_related('user', 'slot'):
        writer.writerow([str(b.id)[:8], b.user.car_number, b.slot.slot_code,
                         b.date, b.entry_time, b.exit_time, b.vehicle_type,
                         round(b.hours_booked, 2), b.base_charge, b.overstay_charge,
                         b.total_charge, b.status])
    return response


# ─── RATE SETTINGS ───────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def rate_settings(request):
    if request.user.role != 'Admin':
        return Response({'error': 'Admin only'}, status=403)
    if request.method == 'GET':
        return Response({
            'rates': settings.PARKING_RATES,
            'overstay_penalty': settings.OVERSTAY_PENALTY_RATE,
        })

    rates = request.data.get('rates')
    overstay_penalty = request.data.get('overstay_penalty')
    if isinstance(rates, dict):
        settings.PARKING_RATES.update(rates)
    if overstay_penalty is not None:
        try:
            settings.OVERSTAY_PENALTY_RATE = float(overstay_penalty)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid overstay_penalty value'}, status=400)

    return Response({
        'message': 'Rates updated',
        'rates': settings.PARKING_RATES,
        'overstay_penalty': settings.OVERSTAY_PENALTY_RATE,
    })

# ─── HEALTH CHECK ──────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"status": "ok"})