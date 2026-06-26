from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from bookings.models import Booking, Purchase
from listings.models import Listing
from accounts.models import User
from payments.models import Payout, FeaturedSubscription

@staff_member_required
def admin_dashboard(request):
    # Basic counts
    total_listings = Listing.objects.count()
    pending_listings = Listing.objects.filter(status='pending').count()
    total_users = User.objects.count()
    total_bookings = Booking.objects.count()
    total_purchases = Purchase.objects.count()

    # Commission earned (total and this month)
    total_commission = Booking.objects.aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0
    total_commission += Purchase.objects.aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0

    this_month = timezone.now().replace(day=1)
    monthly_commission = Booking.objects.filter(paid_at__gte=this_month).aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0
    monthly_commission += Purchase.objects.filter(paid_at__gte=this_month).aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0

    # Pending payouts
    pending_payouts = Payout.objects.filter(status='pending')
    total_pending_payouts = pending_payouts.aggregate(Sum('amount'))['amount__sum'] or 0

    # Expiring featured subscriptions (next 7 days)
    expiring_soon = FeaturedSubscription.objects.filter(
        status='active',
        end_date__lte=timezone.now() + timedelta(days=7)
    ).count()

    # Recent activity
    recent_bookings = Booking.objects.order_by('-paid_at')[:5]
    recent_purchases = Purchase.objects.order_by('-paid_at')[:5]

    context = {
        'total_listings': total_listings,
        'pending_listings': pending_listings,
        'total_users': total_users,
        'total_bookings': total_bookings,
        'total_purchases': total_purchases,
        'total_commission': total_commission,
        'monthly_commission': monthly_commission,
        'total_pending_payouts': total_pending_payouts,
        'expiring_soon': expiring_soon,
        'recent_bookings': recent_bookings,
        'recent_purchases': recent_purchases,
        'pending_payouts': pending_payouts,
    }
    return render(request, 'admin/dashboard.html', context)