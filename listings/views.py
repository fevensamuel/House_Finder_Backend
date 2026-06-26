from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from .models import Listing
from .serializers import ListingSerializer

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    parser_classes = [MultiPartParser, FormParser]   # ✅ support file upload

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        queryset = Listing.objects.filter(status='active')
        # Apply filters
        search = self.request.query_params.get('search')
        city = self.request.query_params.get('city')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        bedrooms = self.request.query_params.get('bedrooms')

        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))
        if city:
            queryset = queryset.filter(city__icontains=city)
        if min_price:
            queryset = queryset.filter(
                Q(price_per_day__gte=min_price) | Q(price_per_month__gte=min_price)
            )
        if max_price:
            queryset = queryset.filter(
                Q(price_per_day__lte=max_price) | Q(price_per_month__lte=max_price)
            )
        if bedrooms:
            queryset = queryset.filter(bedrooms=bedrooms)

        # Featured first
        return queryset.order_by('-is_featured', '-created_at')

    def perform_create(self, serializer):
        serializer.save(landlord=self.request.user)