from django.urls import path
from .views import login_view, register_view, change_password, my_profile, update_profile
from .auth_views import logout_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('change-password/', change_password, name='change-password'),
    path('logout/', logout_view, name='logout'),
    path('profile/', my_profile, name='my-profile'),
    path('profile/update/', update_profile, name='update-profile'),
]
