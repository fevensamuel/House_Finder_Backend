# refunds/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from bookings.models import Booking  # only Booking
from .models import RefundRequest
from .serializers import RefundRequestSerializer
from notifications import send_push_notification

class CreateRefundRequestView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        booking_id = request.data.get('booking_id')
        description = request.data.get('description')
        misleading_photos = request.FILES.getlist('misleading_photos')
        reality_photos = request.FILES.getlist('reality_photos')

        if not description:
            return Response({'error': 'Description is required'}, status=400)

        if len(misleading_photos) < 2 or len(reality_photos) < 2:
            return Response({'error': 'Please upload at least 2 misleading photos and 2 reality photos'}, status=400)

        booking = get_object_or_404(Booking, id=booking_id, customer=request.user, status='paid')
        if RefundRequest.objects.filter(booking=booking).exists():
            return Response({'error': 'You have already submitted a refund request for this booking.'}, status=400)
        if timezone.now() > booking.paid_at + timedelta(days=3):
            return Response({'error': 'Refund window has expired (3 days after payment)'}, status=400)

        # In production, save files properly; here we store names as placeholders
        misleading_urls = [img.name for img in misleading_photos]
        reality_urls = [img.name for img in reality_photos]

        landlord = booking.listing.landlord

        refund = RefundRequest.objects.create(
            booking=booking,
            customer=request.user,
            landlord=landlord,
            misleading_photos=misleading_urls,
            reality_photos=reality_urls,
            description=description,
            status='pending'
        )

        serializer = RefundRequestSerializer(refund)
        return Response(serializer.data, status=201)

class MyRefundRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        refunds = RefundRequest.objects.filter(customer=request.user)
        serializer = RefundRequestSerializer(refunds, many=True)
        return Response(serializer.data)

class LandlordRefundRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'landlord':
            return Response({'error': 'Only landlords can view'}, status=403)
        refunds = RefundRequest.objects.filter(landlord=request.user)
        serializer = RefundRequestSerializer(refunds, many=True)
        return Response(serializer.data)