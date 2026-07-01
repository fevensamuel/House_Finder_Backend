# bookings/models.py
from django.db import models
from accounts.models import User
from listings.models import Listing

class Booking(models.Model):
    STATUS_CHOICES = (
    ('paid', 'Paid'),
    ('cancelled', 'Cancelled'),
    ('completed', 'Completed'),
    ('cancellation_requested', 'Cancellation Requested'),  # new
)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings_as_customer')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    months = models.PositiveIntegerField()
    total_rent = models.DecimalField(max_digits=12, decimal_places=2)
    customer_commission = models.DecimalField(max_digits=12, decimal_places=2)
    landlord_commission = models.DecimalField(max_digits=12, decimal_places=2)
    total_paid = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='paid')
    payment_reference = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)
    google_maps_revealed = models.BooleanField(default=False)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='paid')

    def __str__(self):
        return f"Booking #{self.id} - {self.listing.title}"
