from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'listing', 'start_date', 'end_date', 'total_amount', 'status')
    list_filter = ('status', 'start_date')
    search_fields = ('customer__display_name', 'listing__title')