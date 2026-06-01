from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('landlord', 'Landlord'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, unique=True)
    display_name = models.CharField(max_length=100)
    national_id_number = models.CharField(max_length=20, blank=True, null=True)
    fayda_fin = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    # avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    # Pending edits (require admin approval)
    pending_display_name = models.CharField(max_length=100, blank=True, null=True)
    pending_phone = models.CharField(max_length=15, blank=True, null=True)
    pending_national_id = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.display_name} ({self.role})"