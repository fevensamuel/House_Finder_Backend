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
            'price_per_month', 'sale_price',
            'city', 'address', 'google_maps_link',
            'bedrooms', 'bathrooms', 'kitchen', 'living_room',
            'status', 'is_featured', 'featured_until', 'created_at', 'updated_at',
            'images', 'uploaded_images', 'uploaded_room_types',
            'availability', 'penalty_amount'
        )
        read_only_fields = ('landlord', 'status', 'is_featured', 'featured_until', 'created_at', 'updated_at')

    def get_penalty_amount(self, obj):
        try:
            from payments.utils import calculate_commission
            base = obj.sale_price or obj.price_per_month
            if not base:
                return 0
            commission = calculate_commission(base)
            return float(base + commission)
        except Exception:
            return 0

    def validate_images(self, data, images, room_types):
        # Helper to validate images – only called on create/update
        if not images:
            return  # no images to validate
        if len(images) != len(room_types):
            raise serializers.ValidationError("Number of images and room types must match.")

        bedrooms = data.get('bedrooms', 0)
        bathrooms = data.get('bathrooms', 0)
        kitchen = data.get('kitchen', 1)
        living_room = data.get('living_room', 1)

        required = {'overall': 2}
        if kitchen > 0:
            required['kitchen'] = 1
        if living_room > 0:
            required['living_room'] = 1
        for i in range(1, bedrooms + 1):
            required[f'bedroom_{i}'] = 1
        for i in range(1, bathrooms + 1):
            required[f'bathroom_{i}'] = 1

        count_dict = {}
        for rt in room_types:
            count_dict[rt] = count_dict.get(rt, 0) + 1

        for room_type, min_count in required.items():
            if count_dict.get(room_type, 0) < min_count:
                raise serializers.ValidationError(
                    f"Room type '{room_type}' requires at least {min_count} image(s)."
                )
        for room_type, count in count_dict.items():
            if count > 2:
                raise serializers.ValidationError(
                    f"Room type '{room_type}' can have at most 2 images."
                )

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        uploaded_room_types = validated_data.pop('uploaded_room_types', [])
        # Validate images (if any)
        if uploaded_images:
            self.validate_images(validated_data, uploaded_images, uploaded_room_types)
        listing = Listing.objects.create(**validated_data)
        for img, rt in zip(uploaded_images, uploaded_room_types):
            ListingImage.objects.create(listing=listing, image=img, room_type=rt)
        return listing

    def update(self, instance, validated_data):
        # For simplicity, we don't handle image updates via this serializer
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance