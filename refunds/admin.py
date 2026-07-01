from django.contrib import admin
from .models import RefundRequest

@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'landlord', 'status', 'refund_amount', 'is_within_window', 'created_at')
    list_filter = ('status', 'created_at')
    readonly_fields = ('refund_amount',)
    actions = ['approve_refund', 'deny_refund']

    def approve_refund(self, request, queryset):
        for refund in queryset:
            refund.status = 'approved'
            refund.save()
        self.message_user(request, f"{queryset.count()} refund(s) approved.")
    approve_refund.short_description = "Approve selected refunds"

    def deny_refund(self, request, queryset):
        for refund in queryset:
            refund.status = 'denied'
            refund.save()
        self.message_user(request, f"{queryset.count()} refund(s) denied.")
    deny_refund.short_description = "Deny selected refunds"