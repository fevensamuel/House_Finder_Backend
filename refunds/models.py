from django.db import models
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from bookings.models import Booking  # only Booking

class RefundRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('completed', 'Refund Completed'),
    )
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='refund_requests')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refund_requests')
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='landlord_refund_requests')
    misleading_photos = models.JSONField(default=list)
    reality_photos = models.JSONField(default=list)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    @property
    def refund_amount(self):
        return self.booking.total_paid if self.booking else 0

    @property
    def is_within_window(self):
        if self.booking and self.booking.paid_at:
            return timezone.now() <= self.booking.paid_at + timedelta(days=3)
        return False

    def __str__(self):
        return f"Refund #{self.id} - {self.customer.display_name}"