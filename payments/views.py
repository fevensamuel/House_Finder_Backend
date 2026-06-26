import uuid
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Sum

from .models import Payment, FeaturedSubscription, Payout
from .utils import calculate_commission, get_featured_price
from .chapa import initialize_payment, verify_payment
from bookings.models import Booking, Purchase, BookingExtension
from listings.models import Listing
from notifications import send_push_notification


# ---------- GENERIC PAYMENT INITIATION (booking / purchase) ----------
class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        booking_id = request.data.get('booking_id')
        purchase_id = request.data.get('purchase_id')
        obj = None

        if booking_id:
            obj = get_object_or_404(Booking, id=booking_id, customer=request.user, status='paid')
        elif purchase_id:
            obj = get_object_or_404(Purchase, id=purchase_id, customer=request.user, status='paid')
        else:
            return Response({'error': 'booking_id or purchase_id required'}, status=400)

        amount = float(obj.total_amount)
        tx_ref = f"tx-{uuid.uuid4().hex[:10]}"
        email = request.user.email
        return_url = "betrent://payment-success"
        callback_url = "https://yourdomain.com/api/v1/payments/webhook/"

        result = initialize_payment(amount, email, tx_ref, callback_url, return_url)
        if result.get('status') == 'success':
            Payment.objects.create(
                booking=obj if booking_id else None,
                purchase=obj if purchase_id else None,
                amount=amount,
                chapa_tx_ref=tx_ref,
                status='pending'
            )
            return Response({'checkout_url': result['data']['checkout_url'], 'tx_ref': tx_ref})
        return Response({'error': 'Payment initiation failed'}, status=400)


# ---------- PAYMENT VERIFICATION (handles booking, purchase, extension) ----------
class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, tx_ref):
        result = verify_payment(tx_ref)
        if result.get('status') != 'success':
            return Response({'status': 'failed', 'message': 'Payment not successful'}, status=400)

        payment = get_object_or_404(Payment, chapa_tx_ref=tx_ref)
        payment.status = 'completed'
        payment.save()

        # ----- Booking -----
        if payment.booking:
            booking = payment.booking
            booking.status = 'paid'
            booking.save()
            # Create payout record for landlord
            Payout.objects.get_or_create(
                booking=booking,
                landlord=booking.listing.landlord,
                defaults={'amount': booking.rent_amount, 'status': 'pending'}
            )
            # Push notification to landlord
            send_push_notification(
                user=booking.listing.landlord,
                title="Booking Paid",
                body=f"{booking.customer.display_name} confirmed booking for {booking.listing.title} from {booking.start_date} to {booking.end_date}",
                data={"booking_id": str(booking.id), "type": "booking"}
            )

        # ----- Purchase -----
        elif payment.purchase:
            purchase = payment.purchase
            purchase.status = 'paid'
            purchase.save()
            Payout.objects.get_or_create(
                purchase=purchase,
                landlord=purchase.listing.landlord,
                defaults={'amount': purchase.sale_price, 'status': 'pending'}
            )
            send_push_notification(
                user=purchase.listing.landlord,
                title="Property Sold!",
                body=f"{purchase.customer.display_name} bought {purchase.listing.title} for {purchase.total_amount} ETB",
                data={"purchase_id": str(purchase.id), "type": "purchase"}
            )

        # ----- Extension -----
        elif payment.extension:
            extension = payment.extension
            extension.status = 'paid'
            extension.paid_at = timezone.now()
            extension.save()
            # Update the original booking's end date
            booking = extension.booking
            booking.end_date = extension.new_end_date
            booking.save()
            # Optional: create payout for the extra rent
            Payout.objects.get_or_create(
                extension=extension,
                landlord=booking.listing.landlord,
                defaults={'amount': extension.additional_rent, 'status': 'pending'}
            )
            send_push_notification(
                user=booking.listing.landlord,
                title="Booking Extended",
                body=f"{booking.customer.display_name} extended {booking.listing.title} by {extension.extra_days} days",
                data={"booking_id": str(booking.id), "type": "extension"}
            )

        return Response({'status': 'success', 'message': 'Payment verified'})


# ---------- FEATURED LISTINGS (bulk) ----------
class InitiateFeaturedPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        listing_ids = request.data.get('listing_ids', [])
        plan = request.data.get('plan')   # 'monthly' or 'yearly'

        if not listing_ids or not plan:
            return Response({'error': 'listing_ids and plan required'}, status=400)

        listings = Listing.objects.filter(id__in=listing_ids, landlord=request.user)
        if listings.count() != len(listing_ids):
            return Response({'error': 'One or more listings not found or not yours'}, status=404)

        quantity = len(listing_ids)
        total_amount = get_featured_price(plan, quantity)

        tx_ref = f"featured-{uuid.uuid4().hex[:10]}"
        result = initialize_payment(
            amount=total_amount,
            email=request.user.email,
            tx_ref=tx_ref,
            callback_url="https://yourdomain.com/api/v1/payments/featured-webhook/",
            return_url="betrent://featured-success"
        )

        if result.get('status') == 'success':
            end_date = timezone.now() + timedelta(days=30 if plan == 'monthly' else 365)
            sub = FeaturedSubscription.objects.create(
                landlord=request.user,
                plan=plan,
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


# ---------- ADMIN STATS & CASH FLOW ----------
class AdminStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from bookings.models import Booking, Purchase
        total_commission = Booking.objects.aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0
        total_commission += Purchase.objects.aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0
        pending_payouts = Payout.objects.filter(status='pending').values(
            'id', 'landlord__display_name', 'amount', 'booking__id', 'purchase__id'
        )
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