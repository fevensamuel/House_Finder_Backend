# bookings/urls.py
from django.urls import path
from .views import (
    CreateBookingView, MyBookingsView, LandlordTransactionsView, CancelBookingView
)

urlpatterns = [
    path('bookings/', CreateBookingView.as_view()),
    path('bookings/my/', MyBookingsView.as_view()),
    path('transactions/', LandlordTransactionsView.as_view()),
    path('bookings/<int:booking_id>/cancel/', CancelBookingView.as_view()),
]