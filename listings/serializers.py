from rest_framework import serializers
from .models import Listing, ListingImage

class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ('id', 'image')

class ListingSerializer(serializers.ModelSerializer):
    images = ListingImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    landlord_name = serializers.CharField(source='landlord.display_name', read_only=True)
    
    class Meta:
        model = Listing
        fields = ('id', 'landlord', 'landlord_name', 'title', 'description', 
                  'price_per_day', 'price_per_month', 'city', 'address', 
                  'google_maps_link', 'bedrooms', 'bathrooms', 'kitchen', 'living_room',
                  'status', 'is_featured', 'created_at', 'images', 'uploaded_images')
        read_only_fields = ('landlord', 'status', 'is_featured', 'created_at')
    
    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        listing = Listing.objects.create(**validated_data)
        for img in uploaded_images:
            ListingImage.objects.create(listing=listing, image=img)
        return listing