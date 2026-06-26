from rest_framework import serializers
from .models import Listing, ListingImage

class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ('id', 'image', 'uploaded_at')
        read_only_fields = ('uploaded_at',)

class ListingSerializer(serializers.ModelSerializer):
    images = ListingImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),   # accepts image files
        write_only=True,
        required=False
    )
    landlord_name = serializers.CharField(source='landlord.display_name', read_only=True)
    availability = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = (
            'id', 'landlord', 'landlord_name', 'title', 'description',
            'price_per_day', 'price_per_month', 'sale_price',
            'city', 'address', 'google_maps_link',
            'bedrooms', 'bathrooms', 'kitchen', 'living_room',
            'status', 'is_featured', 'featured_until', 'created_at', 'updated_at',
            'images', 'uploaded_images', 'availability'
        )
        read_only_fields = ('landlord', 'status', 'is_featured', 'featured_until', 'created_at', 'updated_at')

    def get_availability(self, obj):
        return obj.get_availability()

    def validate(self, data):
        price_per_day = data.get('price_per_day')
        price_per_month = data.get('price_per_month')
        if price_per_month and not price_per_day:
            data['price_per_day'] = round(price_per_month / 30, 2)
        elif price_per_day and not price_per_month:
            data['price_per_month'] = round(price_per_day * 30, 2)
        return data

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        listing = Listing.objects.create(**validated_data)
        for img in uploaded_images:
            ListingImage.objects.create(listing=listing, image=img)
        return listing

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if uploaded_images is not None:
            # Optional: clear existing images or just add new ones
            # For simplicity, add new ones:
            for img in uploaded_images:
                ListingImage.objects.create(listing=instance, image=img)
        return instance