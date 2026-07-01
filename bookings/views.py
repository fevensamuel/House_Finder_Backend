from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
import uuid

from .models import Booking
from .serializers import BookingSerializer
from listings.models import Listing
from payments.utils import calculate_commission
from payments.chapa import initialize_payment
from payments.models import Payment
from notifications import send_push_notification


# ---------- RENTAL BOOKING ----------
class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        listing_id = request.data.get('listing_id')
        months = request.data.get('months')

        if not listing_id or not months:
            return Response({'error': 'listing_id and months required'}, status=400)

        try:
            months = int(months)
        except ValueError:
            return Response({'error': 'months must be an integer'}, status=400)

        if months < 2 or months > 12:
            return Response({'error': 'Months must be between 2 and 12'}, status=400)

        listing = get_object_or_404(Listing, id=listing_id, status='active')
        if not listing.price_per_month:
            return Response({'error': 'This listing is not available for rent'}, status=400)

        total_rent = listing.price_per_month * months
        customer_commission = calculate_commission(total_rent)
        landlord_commission = calculate_commission(total_rent)
        total_paid = total_rent + customer_commission

        booking = Booking.objects.create(
            customer=request.user,
            listing=listing,
            months=months,
            total_rent=total_rent,
            customer_commission=customer_commission,
            landlord_commission=landlord_commission,
            total_paid=total_paid,
            status='paid'  # will be updated after payment
        )

        # Send push notification to landlord (optional)
        send_push_notification(
            user=listing.landlord,
            title="New Booking Request!",
            body=f"{request.user.display_name} wants to book {listing.title} for {months} months",
            data={"booking_id": str(booking.id), "type": "booking"}
        )

        return Response(BookingSerializer(booking).data, status=201)


class MyBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(customer=request.user).order_by('-paid_at')
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


# ---------- CANCEL BOOKING ----------
class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, customer=request.user, status='paid')
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found or not eligible for cancellation'}, status=404)

        # Check if cancellation is within 3 days (optional)
        # if timezone.now() > booking.paid_at + timedelta(days=3):
        #     return Response({'error': 'Cancellation window expired'}, status=400)

        # Calculate refund: total_paid - 2 * commission
        refund = booking.total_paid - (booking.customer_commission * 2)
        if refund < 0:
            refund = 0  # ensure non-negative

        # Update booking status to 'cancellation_requested'
        booking.status = 'cancellation_requested'
        booking.refund_amount = refund
        booking.cancelled_at = timezone.now()
        booking.save()

        # Optionally create a RefundRequest record here if you have that model

        # Notify landlord (optional)
        send_push_notification(
            user=booking.listing.landlord,
            title="Booking Cancellation Requested",
            body=f"{booking.customer.display_name} requested cancellation of {booking.listing.title}",
            data={"booking_id": str(booking.id), "type": "cancellation"}
        )

        return Response({
            'status': 'cancellation_requested',
            'refund_amount': refund,
            'message': 'Cancellation request submitted for admin approval.'
        })

    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, customer=request.user, status='paid')
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found or not eligible'}, status=404)

       
        
# ---------- LANDLORD TRANSACTIONS ----------
class LandlordTransactionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'landlord':
            return Response({'error': 'Only landlords can view transactions'}, status=403)

        bookings = Booking.objects.filter(listing__landlord=user).order_by('-paid_at')
        result = []

        for b in bookings:
            result.append({
                'type': 'rent',
                'id': b.id,
                'customer': {
                    'name': b.customer.display_name,
                    'phone': b.customer.phone,
                    'id_document_front': b.customer.id_document_front.url if b.customer.id_document_front else None,
                    'has_id_document': bool(b.customer.id_document_front),
                },
                'raw_amount': float(b.total_rent),
                'months': b.months,
                'commission_deducted': float(b.landlord_commission),
                'net_payout': float(b.total_rent - b.landlord_commission),
                'status': b.status,
                'paid_at': b.paid_at,
            })

        result.sort(key=lambda x: x['paid_at'], reverse=True)
        return Response(result)