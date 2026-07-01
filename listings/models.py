from django.db import models
from django.utils import timezone
from accounts.models import User

DISTRICT_CHOICES = [
    ('Addis Ababa', 'Addis Ababa (General/Central)'),
    ('Bole', 'Bole, Addis Ababa'),
    ('CMC', 'CMC, Addis Ababa'),
    ('Kazanchis', 'Kazanchis, Addis Ababa'),
    ('Old Airport', 'Old Airport, Addis Ababa'),
    ('Mexico', 'Mexico, Addis Ababa'),
    ('Ayat', 'Ayat, Addis Ababa'),
    ('Summit', 'Summit, Addis Ababa'),
    ('Lideta', 'Lideta, Addis Ababa'),
    ('Sarbet', 'Sarbet, Addis Ababa'),
]

CATEGORY_CHOICES = [
    ('Apartment', 'Apartment'),
    ('House', 'House'),
    ('Villa', 'Villa'),
    ('Studio', 'Studio'),
]

class Listing(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('booked', 'Booked'),
        ('hidden', 'Hidden by Admin'),
        ('sold', 'Sold'),
    )
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    city = models.CharField(max_length=50, choices=DISTRICT_CHOICES, default='Addis Ababa')
    address = models.CharField(max_length=255)
    google_maps_link = models.URLField(blank=True, null=True)
    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=0)
    kitchen = models.PositiveIntegerField(default=1)
    living_room = models.PositiveIntegerField(default=1)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Apartment')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False)
    featured_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.title

    # ... rest (penalty_amount, get_availability)
    @property
    def penalty_amount(self):
        from payments.utils import calculate_commission
        base = self.sale_price or self.price_per_month
        if not base:
            return 0
        commission = calculate_commission(base)
        return base + commission

    def get_availability(self):
        return {
            'is_available': True,
            'current_booking_end': None,
            'next_available_from': None,
            'booked_ranges': [],
        }

class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listings/')
    room_type = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.listing.title} - {self.room_type}"