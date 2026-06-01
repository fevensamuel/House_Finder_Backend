from django.db import models
from bookings.models import Booking
from accounts.models import User

class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    chapa_tx_ref = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class Payout(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payouts')
    landlord = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    telebirr_reference = models.CharField(max_length=100, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)