from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'listing', 'months', 'total_paid', 'status', 'paid_at')
    list_filter = ('status', 'paid_at')
    search_fields = ('customer__display_name', 'listing__title')
