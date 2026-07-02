# listings/serializers.py
from rest_framework import serializers
from .models import Listing, ListingImage

class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ('id', 'image', 'room_type', 'uploaded_at')
        read_only_fields = ('uploaded_at',)

class ListingSerializer(serializers.ModelSerializer):
    images = ListingImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    uploaded_room_types = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    landlord_name = serializers.CharField(source='landlord.display_name', read_only=True)
    availability = serializers.SerializerMethodField()
    penalty_amount = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = (
            'id', 'landlord', 'landlord_name', 'title', 'description',
            'price_per_month',  # ✅ removed sale_price
            'city', 'address', 'google_maps_link',
            'bedrooms', 'bathrooms', 'kitchen', 'living_room',
            'status', 'is_featured', 'featured_until', 'created_at', 'updated_at',
            'images', 'uploaded_images', 'uploaded_room_types',
            'availability', 'penalty_amount'
        )
        read_only_fields = ('landlord', 'status', 'is_featured', 'featured_until', 'created_at', 'updated_at')

    def get_availability(self, obj):
        return obj.get_availability()

    def get_penalty_amount(self, obj):
        try:
            from payments.utils import calculate_commission
            base = obj.price_per_month
            if not base:
                return 0
            commission = calculate_commission(base)
            return float(base + commission * 2)
        except Exception:
            return 0

    def validate_images(self, data, images, room_types):
        # ... keep validation logic unchanged ...
        pass

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        uploaded_room_types = validated_data.pop('uploaded_room_types', [])
        if uploaded_images:
            self.validate_images(validated_data, uploaded_images, uploaded_room_types)
        listing = Listing.objects.create(**validated_data)
        for img, rt in zip(uploaded_images, uploaded_room_types):
            ListingImage.objects.create(listing=listing, image=img, room_type=rt)
        return listing

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance