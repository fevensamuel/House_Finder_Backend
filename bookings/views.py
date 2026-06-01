from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Booking
from .serializers import BookingSerializer
from listings.models import Listing
from payments.utils import calculate_commission

class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        listing_id = request.data.get('listing_id')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        try:
            listing = Listing.objects.get(id=listing_id, status='active')
        except Listing.DoesNotExist:
            return Response({'error': 'Listing not found or not active'}, status=404)
        
        # Calculate days
        days = (timezone.datetime.strptime(end_date, '%Y-%m-%d') - 
                timezone.datetime.strptime(start_date, '%Y-%m-%d')).days
        if days <= 0:
            days = 1
        
        # Use price_per_day if available, else price_per_month divided by 30
        if listing.price_per_day:
            rent_amount = listing.price_per_day * days
        else:
            rent_amount = (listing.price_per_month / 30) * days
        
        commission_amount = calculate_commission(rent_amount)
        total_amount = rent_amount + commission_amount
        
        booking = Booking.objects.create(
            customer=request.user,
            listing=listing,
            start_date=start_date,
            end_date=end_date,
            rent_amount=rent_amount,
            commission_amount=commission_amount,
            total_amount=total_amount,
            status='paid'  # Will be set to paid after payment verification
        )
        return Response(BookingSerializer(booking).data, status=201)

class MyBookingsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        bookings = Booking.objects.filter(customer=request.user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)