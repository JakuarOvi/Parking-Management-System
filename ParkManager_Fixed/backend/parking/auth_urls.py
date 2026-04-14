from django.urls import path
from .views import login_view, register_view, change_password

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('change-password/', change_password, name='change-password'),
]
