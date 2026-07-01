# payments/admin.py
from django.contrib import admin
from .models import Payment, FeaturedSubscription, Payout

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')

@admin.register(FeaturedSubscription)
class FeaturedSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'landlord', 'quantity', 'total_amount', 'status', 'end_date')
    list_filter = ('status',)
    actions = ['activate_subscription']

    def activate_subscription(self, request, queryset):
        from django.utils import timezone
        for sub in queryset:
            if sub.status == 'pending':
                sub.status = 'active'
                sub.save()
                for listing in sub.listings.all():
                    listing.is_featured = True
                    listing.featured_until = sub.end_date
                    listing.save()
        self.message_user(request, f"{queryset.count()} subscription(s) activated.")
    activate_subscription.short_description = "Activate selected subscriptions"

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'landlord', 'amount', 'status', 'created_at', 'sent_at')
    list_filter = ('status', 'created_at')
    list_editable = ('status',)
    actions = ['mark_as_sent']

    def mark_as_sent(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='sent', sent_at=timezone.now())
        self.message_user(request, f"{queryset.count()} payout(s) marked as sent.")
    mark_as_sent.short_description = "Mark selected payouts as sent"