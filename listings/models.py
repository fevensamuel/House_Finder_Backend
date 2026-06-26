from django.db import models
from django.utils import timezone
from accounts.models import User

class Listing(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('booked', 'Booked'),
        ('hidden', 'Hidden by Admin'),
    )

    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    description = models.TextField()

    # Pricing
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # Location
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    google_maps_link = models.URLField(blank=True, null=True)

    # Room details
    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=0)
    kitchen = models.PositiveIntegerField(default=1)
    living_room = models.PositiveIntegerField(default=1)

    # Status & featured
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False)
    featured_until = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.title

    @property
    def total_rooms(self):
        return self.bedrooms + self.bathrooms + self.kitchen + self.living_room

    def get_availability(self):
        """
        Returns:
            - is_available: bool
            - next_available_from: date or None
            - current_booking_end: date or None
            - booked_ranges: list of {'start': date, 'end': date}
        """
        from bookings.models import Booking
        bookings = self.bookings.filter(status='paid').order_by('start_date')
        booked_ranges = [{'start': b.start_date, 'end': b.end_date} for b in bookings]
        now = timezone.now().date()
        next_available = None
        current_booking_end = None

        for b in bookings:
            if b.start_date <= now <= b.end_date:
                current_booking_end = b.end_date
                next_available = b.end_date
                break
        else:
            # No current booking
            if bookings:
                last_end = max(b.end_date for b in bookings)
                next_available = last_end if last_end > now else now
            else:
                next_available = now

        is_available = (current_booking_end is None)
        return {
            'is_available': is_available,
            'current_booking_end': current_booking_end,
            'next_available_from': next_available,
            'booked_ranges': booked_ranges,
        }


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listings/')   # actual file upload
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.listing.title}"