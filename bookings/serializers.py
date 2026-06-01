from rest_framework import serializers
from .models import Booking
from listings.serializers import ListingSerializer

class BookingSerializer(serializers.ModelSerializer):
    listing_details = ListingSerializer(source='listing', read_only=True)
    
    class Meta:
        model = Booking
        fields = ('id', 'customer', 'listing', 'listing_details', 'start_date', 'end_date',
                  'total_amount', 'rent_amount', 'commission_amount', 'status', 'paid_at')
        read_only_fields = ('customer', 'total_amount', 'rent_amount', 'commission_amount', 'status', 'paid_at')