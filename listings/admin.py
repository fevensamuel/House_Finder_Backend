# listings/admin.py
from django.contrib import admin
from .models import Listing, ListingImage

class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1
    fields = ('image', 'room_type')

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'landlord', 'city', 'category', 'price_per_month', 'status', 'is_featured')  # sale_price removed
    list_filter = ('status', 'city', 'is_featured')
    search_fields = ('title', 'address', 'landlord__display_name')
    inlines = [ListingImageInline]
    actions = ['approve_listings', 'hide_listings']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "landlord":
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(role='landlord')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    fieldsets = (
        (None, {'fields': ('landlord', 'title', 'description', 'category', 'status', 'is_featured')}),
        ('Pricing', {'fields': ('price_per_month',)}),
        ('Location', {'fields': ('city', 'address', 'google_maps_link')}),
        ('Room Counts', {'fields': ('bedrooms', 'bathrooms', 'kitchen', 'living_room')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')

    def approve_listings(self, request, queryset):
        queryset.update(status='active')
        self.message_user(request, f"{queryset.count()} listings approved.")
    approve_listings.short_description = "Approve selected listings"

    def hide_listings(self, request, queryset):
        queryset.update(status='hidden')
        self.message_user(request, f"{queryset.count()} listings hidden.")
    hide_listings.short_description = "Hide selected listings"

@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ('listing', 'room_type', 'uploaded_at')
    list_filter = ('room_type',)