from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('landlord', 'Landlord'),
        ('customer', 'Customer'),
    )

    # Basic fields (we keep username, first_name, last_name but hide them in admin)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    email = models.EmailField(unique=True, blank=False, null=False)
    phone = models.CharField(max_length=15, unique=True)          # already unique
    display_name = models.CharField(max_length=100)
    fayda_fin = models.CharField(max_length=20, unique=True, null=True, blank=True)   # enforce uniqueness
    is_active = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    fcm_token = models.CharField(max_length=255, blank=True, null=True)

    # Financial / wallet fields (from frontend)
    cbe_bank_account = models.CharField(max_length=50, blank=True, null=True)
    telebirr_phone = models.CharField(max_length=20, blank=True, null=True)
    cbe_birr_phone = models.CharField(max_length=20, blank=True, null=True)

    # ID documents – renamed to match frontend
    id_front = models.ImageField(upload_to='user_ids/', null=True, blank=True)
    id_back = models.ImageField(upload_to='user_ids/', null=True, blank=True)

    # Pending changes (used for admin approval workflow)
    pending_display_name = models.CharField(max_length=100, blank=True, null=True)
    pending_phone = models.CharField(max_length=15, blank=True, null=True)

    @property
    def is_profile_complete(self):
        required = [
            self.phone,
            self.fayda_fin,
            self.id_front,
            self.id_back,
            self.cbe_bank_account,
            self.telebirr_phone,
            self.cbe_birr_phone,
        ]
        return all(required)

    def __str__(self):
        return self.email or self.username