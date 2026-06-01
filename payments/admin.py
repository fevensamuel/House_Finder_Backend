from django.contrib import admin
from .models import Payment, Payout

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'status', 'created_at')

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ('booking', 'landlord', 'amount', 'status')