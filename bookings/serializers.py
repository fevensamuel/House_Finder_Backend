from rest_framework import serializers
from .models import Booking, Purchase, BookingExtension
from listings.serializers import ListingSerializer

class BookingSerializer(serializers.ModelSerializer):
    listing_details = ListingSerializer(source='listing', read_only=True)
    
    class Meta:
        model = Booking
        fields = ('id', 'customer', 'listing', 'listing_details', 'start_date', 'end_date',
                  'total_amount', 'rent_amount', 'commission_amount', 'status', 'paid_at')
        read_only_fields = ('customer', 'total_amount', 'rent_amount', 'commission_amount', 'status', 'paid_at')

class PurchaseSerializer(serializers.ModelSerializer):
    listing_details = ListingSerializer(source='listing', read_only=True)
    
    class Meta:
        model = Purchase
        fields = ('id', 'customer', 'listing', 'listing_details', 'total_amount', 
                  'sale_price', 'commission_amount', 'status', 'paid_at')
        read_only_fields = ('customer', 'total_amount', 'sale_price', 'commission_amount', 'status', 'paid_at')

class BookingExtensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingExtension
        fields = '__all__'