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

    def __str__(self):
        return f"Booking {self.id} - {self.listing.title}"

class Purchase(models.Model):
    STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='purchases')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='paid')
    payment_reference = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)
    google_maps_revealed = models.BooleanField(default=False)

    def __str__(self):
        return f"Purchase {self.id} - {self.listing.title}"

class BookingExtension(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='extensions')
    extra_days = models.PositiveIntegerField()
    additional_rent = models.DecimalField(max_digits=10, decimal_places=2)
    additional_commission = models.DecimalField(max_digits=10, decimal_places=2)
    additional_total = models.DecimalField(max_digits=10, decimal_places=2)
    new_end_date = models.DateField()
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Extension for Booking {self.booking.id} (+{self.extra_days} days)"