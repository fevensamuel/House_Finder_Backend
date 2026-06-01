from django.db import models
from accounts.models import User
from listings.models import Listing

class Booking(models.Model):
    STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings_as_customer')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='paid')
    payment_reference = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)
    google_maps_revealed = models.BooleanField(default=False)