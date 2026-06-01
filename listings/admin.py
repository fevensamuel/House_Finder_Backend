from django.contrib import admin
from .models import Listing, ListingImage

class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'price_per_month', 'status', 'is_featured')
    list_filter = ('status', 'city', 'is_featured')
    search_fields = ('title', 'address')
    inlines = [ListingImageInline]

@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ('listing', 'uploaded_at')