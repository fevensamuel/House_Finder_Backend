from django.db import models
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
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    google_maps_link = models.URLField(blank=True, null=True)
    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=0)
    kitchen = models.PositiveIntegerField(default=1)
    living_room = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False)
    featured_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    # Temporary: use URLField to avoid Pillow. Later change to ImageField.
    image_url = models.URLField(max_length=500, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.listing.title}"