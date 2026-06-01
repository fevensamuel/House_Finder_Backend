from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from bookings.models import Booking
from .models import Payment, Payout
from .chapa import initialize_payment, verify_payment
import uuid

class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        booking_id = request.data.get('booking_id')
        try:
            booking = Booking.objects.get(id=booking_id, customer=request.user)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=404)
        
        tx_ref = f"betrent-{uuid.uuid4().hex[:10]}"
        email = request.user.email
        amount = float(booking.total_amount)
        callback_url = "https://yourdomain.com/api/v1/payments/webhook/"
        return_url = "betrent://payment-success"
        
        response = initialize_payment(amount, email, tx_ref, callback_url, return_url)
        if response.get('status') == 'success':
            Payment.objects.create(
                booking=booking,
                amount=amount,
                chapa_tx_ref=tx_ref,
                status='pending'
            )
            return Response({'checkout_url': response['data']['checkout_url'], 'tx_ref': tx_ref})
        return Response({'error': 'Payment initialization failed'}, status=400)

class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, tx_ref):
        result = verify_payment(tx_ref)
        if result.get('status') == 'success':
            try:
                payment = Payment.objects.get(chapa_tx_ref=tx_ref)
                payment.status = 'completed'
                payment.save()
                booking = payment.booking
                booking.status = 'paid'
                booking.save()
                # Create payout record for landlord
                Payout.objects.create(
                    booking=booking,
                    landlord=booking.listing.landlord,
                    amount=booking.rent_amount,
                    status='pending'
                )
                return Response({'status': 'success'})
            except Payment.DoesNotExist:
                return Response({'error': 'Payment record not found'}, status=404)
        return Response({'status': 'failed'}, status=400)