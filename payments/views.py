import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum

from .models import Payment, FeaturedSubscription, Payout
from .utils import calculate_commission, get_featured_price
from .chapa import initialize_payment, verify_payment
from bookings.models import Booking
from listings.models import Listing
from notifications import send_push_notification


# ---------- PAYMENT INITIATION ----------
class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        booking_id = request.data.get('booking_id')
        if not booking_id:
            return Response({'error': 'booking_id required'}, status=400)

        booking = get_object_or_404(Booking, id=booking_id, customer=request.user, status='paid')
        amount = float(booking.total_paid)
        tx_ref = f"tx-{uuid.uuid4().hex[:10]}"
        email = request.user.email
        return_url = "betrent://payment-success"
        callback_url = "https://yourdomain.com/api/v1/payments/webhook/"

        result = initialize_payment(amount, email, tx_ref, callback_url, return_url)
        if result.get('status') == 'success':
            Payment.objects.create(
                booking=booking,
                amount=amount,
                chapa_tx_ref=tx_ref,
                status='pending'
            )
            return Response({'checkout_url': result['data']['checkout_url'], 'tx_ref': tx_ref})
        return Response({'error': 'Payment initiation failed'}, status=400)


# ---------- PAYMENT VERIFICATION ----------
class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, tx_ref):
        result = verify_payment(tx_ref)
        if result.get('status') != 'success':
            return Response({'status': 'failed'}, status=400)

        payment = get_object_or_404(Payment, chapa_tx_ref=tx_ref)
        payment.status = 'completed'
        payment.save()

        if payment.booking:
            booking = payment.booking
            booking.status = 'paid'
            booking.save()
            Payout.objects.get_or_create(
                booking=booking,
                landlord=booking.listing.landlord,
                defaults={'amount': booking.total_rent - booking.landlord_commission, 'status': 'pending'}
            )
            send_push_notification(
                user=booking.listing.landlord,
                title="New Rental Booking!",
                body=f"{booking.customer.display_name} rented {booking.listing.title} for {booking.months} month(s).",
                data={
                    "type": "rent",
                    "customer_name": booking.customer.display_name,
                    "customer_phone": booking.customer.phone,
                    "has_id": str(booking.customer.id_document is not None),
                    "raw_amount": str(booking.total_rent),
                    "months": str(booking.months),
                    "commission": str(booking.landlord_commission),
                    "net_payout": str(booking.total_rent - booking.landlord_commission),
                }
            )
        return Response({'status': 'success'})


# ---------- FEATURED LISTINGS ----------
class InitiateFeaturedPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        listing_ids = request.data.get('listing_ids', [])
        if not listing_ids:
            return Response({'error': 'listing_ids required'}, status=400)

        listings = Listing.objects.filter(id__in=listing_ids, landlord=request.user)
        if listings.count() != len(listing_ids):
            return Response({'error': 'One or more listings not found or not yours'}, status=404)

        quantity = len(listing_ids)
        total_amount = get_featured_price(quantity)

        tx_ref = f"featured-{uuid.uuid4().hex[:10]}"
        result = initialize_payment(
            amount=total_amount,
            email=request.user.email,
            tx_ref=tx_ref,
            callback_url="https://yourdomain.com/api/v1/payments/featured-webhook/",
            return_url="betrent://featured-success"
        )

        if result.get('status') == 'success':
            end_date = timezone.now() + timedelta(days=30)
            sub = FeaturedSubscription.objects.create(
                landlord=request.user,
                quantity=quantity,
                total_amount=total_amount,
                end_date=end_date,
                status='pending',
                payment_reference=tx_ref
            )
            sub.listings.set(listings)
            sub.save()
            Payment.objects.create(
                amount=total_amount,
                chapa_tx_ref=tx_ref,
                status='pending'
            )
            return Response({'checkout_url': result['data']['checkout_url'], 'tx_ref': tx_ref})
        return Response({'error': 'Payment initiation failed'}, status=400)


# ---------- ADMIN STATS & PAYOUTS ----------
class AdminStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_commission = Booking.objects.aggregate(Sum('customer_commission'))['customer_commission__sum'] or 0
        pending_payouts = Payout.objects.filter(status='pending').values('id', 'landlord__display_name', 'amount', 'booking__id')
        return Response({
            'total_commission': total_commission,
            'pending_payouts': list(pending_payouts)
        })


class MarkPayoutSentView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, payout_id):
        payout = get_object_or_404(Payout, id=payout_id)
        payout.status = 'sent'
        payout.sent_at = timezone.now()
        payout.save()
        return Response({'status': 'sent'})