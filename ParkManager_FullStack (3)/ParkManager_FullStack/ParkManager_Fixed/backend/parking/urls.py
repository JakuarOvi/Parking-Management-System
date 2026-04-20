from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny
from . import views

class PublicApiRootRouter(DefaultRouter):
    def get_api_root_view(self, api_urls=None):
        api_root_view = super().get_api_root_view(api_urls=api_urls)
        api_root_view.cls.permission_classes = [AllowAny]
        return api_root_view

router = PublicApiRootRouter()
router.register('slots', views.ParkingSlotViewSet)
router.register('bookings', views.BookingViewSet, basename='booking')
router.register('payments', views.PaymentViewSet, basename='payment')
router.register('staff', views.StaffViewSet)
router.register('shifts', views.ShiftScheduleViewSet)
router.register('notifications', views.NotificationViewSet, basename='notification')
router.register('subscriptions', views.SubscriptionViewSet, basename='subscription')
router.register('lost-found', views.LostFoundViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/user/', views.user_dashboard),
    path('dashboard/admin/', views.admin_dashboard),
    path('slots/blueprint/', views.slot_blueprint),
    path('bookings/scan-qr/', views.scan_qr),
    path('payments/create/', views.create_payment),
    path('reports/', views.reports_data),
    path('reports/export-csv/', views.export_csv),
    path('settings/rates/', views.rate_settings),
    path('health/', views.health_check),
]
