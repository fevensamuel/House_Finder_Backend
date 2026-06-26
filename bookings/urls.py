from django.urls import path
from .views import (
    CreateBookingView, MyBookingsView,
    CreatePurchaseView, MyPurchasesView,
    ExtendBookingView
)

urlpatterns = [
    path('bookings/', CreateBookingView.as_view()),
    path('bookings/my/', MyBookingsView.as_view()),
    path('purchases/', CreatePurchaseView.as_view()),
    path('purchases/my/', MyPurchasesView.as_view()),
    path('bookings/<int:booking_id>/extend/', ExtendBookingView.as_view()),
]