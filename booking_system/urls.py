from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),  # Add this line
    path('contact/', views.contact_view, name='contact'),
    path('offers/', views.offers_view, name='offers'),
    path('claim-reward/<int:reward_id>/', views.claim_reward, name='claim_reward'),
    path('check-reward-code/', views.check_reward_code, name='check_reward_code'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
]