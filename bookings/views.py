from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from datetime import datetime
import uuid

from .models import Booking, Purchase, BookingExtension
from .serializers import BookingSerializer, PurchaseSerializer, BookingExtensionSerializer
from listings.models import Listing
from payments.utils import calculate_commission
from payments.chapa import initialize_payment
from payments.models import Payment
from notifications import send_push_notification


# ---------- RENTAL BOOKING (SMART PRICING) ----------
class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        listing_id = request.data.get('listing_id')
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')

        if not all([listing_id, start_date_str, end_date_str]):
            return Response({'error': 'listing_id, start_date, end_date required'}, status=400)

        try:
            listing = Listing.objects.get(id=listing_id, status='active')
        except Listing.DoesNotExist:
            return Response({'error': 'Listing not found or not active'}, status=404)

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

        if start_date >= end_date:
            return Response({'error': 'End date must be after start date'}, status=400)

        # Availability check
        conflicting = Booking.objects.filter(
            listing=listing,
            status='paid',
            start_date__lt=end_date,
            end_date__gt=start_date
        ).exists()
        if conflicting:
            return Response({'error': 'These dates are already booked'}, status=400)

        days = (end_date - start_date).days
        if days <= 0:
            days = 1

        # Smart pricing: choose daily rate based on duration
        if days >= 30:
            # Use discounted monthly rate if available
            if listing.price_per_month:
                daily_rate = listing.price_per_month / 30
            elif listing.price_per_day:
                daily_rate = listing.price_per_day
            else:
                return Response({'error': 'No rental price available'}, status=400)
        else:
            # Use premium daily rate if available, otherwise monthly/30
            if listing.price_per_day:
                daily_rate = listing.price_per_day
            elif listing.price_per_month:
                daily_rate = listing.price_per_month / 30
            else:
                return Response({'error': 'No rental price available'}, status=400)

        rent_amount = daily_rate * days
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
            status='paid'   # will change after payment
        )

        return Response(BookingSerializer(booking).data, status=201)


class MyBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(customer=request.user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


# ---------- PURCHASE (ONE‑TIME) ----------
class CreatePurchaseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        listing_id = request.data.get('listing_id')
        try:
            listing = Listing.objects.get(id=listing_id, status='active')
        except Listing.DoesNotExist:
            return Response({'error': 'Listing not found or not active'}, status=404)

        if not listing.sale_price:
            return Response({'error': 'This listing is not for sale'}, status=400)

        sale_price = listing.sale_price
        commission_amount = calculate_commission(sale_price)
        total_amount = sale_price + commission_amount

        purchase = Purchase.objects.create(
            customer=request.user,
            listing=listing,
            sale_price=sale_price,
            commission_amount=commission_amount,
            total_amount=total_amount,
            status='paid'
        )

        send_push_notification(
            user=listing.landlord,
            title="New Purchase!",
            body=f"{request.user.display_name} wants to buy {listing.title} for {total_amount} ETB",
            data={"purchase_id": str(purchase.id), "type": "purchase"}
        )

        return Response(PurchaseSerializer(purchase).data, status=201)


class MyPurchasesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        purchases = Purchase.objects.filter(customer=request.user)
        serializer = PurchaseSerializer(purchases, many=True)
        return Response(serializer.data)


# ---------- EXTEND RENTAL (CONSISTENT WITH ORIGINAL BOOKING) ----------
class ExtendBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, customer=request.user, status='paid')
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found or not eligible'}, status=404)

        # Check if there is a future booking starting right after this one
        next_booking = Booking.objects.filter(
            listing=booking.listing,
            status='paid',
            start_date__gte=booking.end_date
        ).exclude(id=booking.id).order_by('start_date').first()
        if next_booking and next_booking.start_date <= booking.end_date:
            return Response({'error': 'Cannot extend – another customer has already booked after your stay.'}, status=400)

        new_end_date_str = request.data.get('new_end_date')
        if not new_end_date_str:
            return Response({'error': 'new_end_date required'}, status=400)

        try:
            new_end_date = datetime.strptime(new_end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

        if new_end_date <= booking.end_date:
            return Response({'error': 'New end date must be after current end date'}, status=400)

        # Ensure no overlap with other bookings
        conflict = Booking.objects.filter(
            listing=booking.listing,
            status='paid',
            start_date__lt=new_end_date,
            end_date__gt=booking.end_date
        ).exclude(id=booking.id).exists()
        if conflict:
            return Response({'error': 'New dates conflict with another booking'}, status=400)

        extra_days = (new_end_date - booking.end_date).days
        listing = booking.listing

        # Determine the daily rate that was used for the original booking
        original_days = (booking.end_date - booking.start_date).days
        if original_days >= 30:
            # Original booking used monthly discount
            if listing.price_per_month:
                daily_rate = listing.price_per_month / 30
            elif listing.price_per_day:
                daily_rate = listing.price_per_day
            else:
                return Response({'error': 'No rental price available'}, status=400)
        else:
            # Original booking used daily rate (premium if set)
            if listing.price_per_day:
                daily_rate = listing.price_per_day
            elif listing.price_per_month:
                daily_rate = listing.price_per_month / 30
            else:
                return Response({'error': 'No rental price available'}, status=400)

        additional_rent = daily_rate * extra_days
        additional_commission = calculate_commission(additional_rent)
        additional_total = additional_rent + additional_commission

        extension = BookingExtension.objects.create(
            booking=booking,
            extra_days=extra_days,
            additional_rent=additional_rent,
            additional_commission=additional_commission,
            additional_total=additional_total,
            new_end_date=new_end_date,
            status='pending'
        )

        tx_ref = f"extend-{uuid.uuid4().hex[:10]}"
        result = initialize_payment(
            amount=float(additional_total),
            email=request.user.email,
            tx_ref=tx_ref,
            callback_url="https://yourdomain.com/api/v1/payments/extension-webhook/",
            return_url="betrent://extension-success"
        )

        if result.get('status') == 'success':
            extension.payment_reference = tx_ref
            extension.save()
            Payment.objects.create(
                extension=extension,
                amount=additional_total,
                chapa_tx_ref=tx_ref,
                status='pending'
            )
            return Response({'checkout_url': result['data']['checkout_url'], 'extension_id': extension.id})
        else:
            extension.delete()
            return Response({'error': 'Payment initiation failed'}, status=400)