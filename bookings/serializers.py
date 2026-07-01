# bookings/serializers.py
from rest_framework import serializers
from .models import Booking
from listings.serializers import ListingSerializer

class BookingSerializer(serializers.ModelSerializer):
    listing_details = ListingSerializer(source='listing', read_only=True)
    class Meta:
        model = Booking
        fields = (
            'id', 'customer', 'listing', 'listing_details', 'months', 'total_rent',
            'customer_commission', 'landlord_commission', 'total_paid', 'status',
            'payment_reference', 'paid_at', 'google_maps_revealed'
        )
        read_only_fields = ('customer', 'total_rent', 'customer_commission',
                            'landlord_commission', 'total_paid', 'paid_at')

