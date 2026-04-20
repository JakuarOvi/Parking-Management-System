from django.urls import path
from .views import login_view, register_view, change_password, logout_view, my_profile, update_profile

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('change-password/', change_password, name='change-password'),
    path('logout/', logout_view, name='logout'),
    path('profile/', my_profile, name='my-profile'),
    path('profile/update/', update_profile, name='update-profile'),
]
