from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from bookings.models import Booking
from listings.models import Listing
from accounts.models import User
from .models import Payout, FeaturedSubscription

@staff_member_required
def admin_dashboard(request):
    total_listings = Listing.objects.count()
    pending_listings = Listing.objects.filter(status='pending').count()
    total_users = User.objects.count()
    total_bookings = Booking.objects.count()

    total_commission = Booking.objects.aggregate(Sum('customer_commission'))['customer_commission__sum'] or 0

    this_month = timezone.now().replace(day=1)
    monthly_commission = Booking.objects.filter(paid_at__gte=this_month).aggregate(Sum('customer_commission'))['customer_commission__sum'] or 0

    pending_payouts = Payout.objects.filter(status='pending')
    total_pending_payouts = pending_payouts.aggregate(Sum('amount'))['amount__sum'] or 0

    expiring_soon = FeaturedSubscription.objects.filter(
        status='active',
        end_date__lte=timezone.now() + timedelta(days=7)
    ).count()

    recent_bookings = Booking.objects.order_by('-paid_at')[:5]

    context = {
        'total_listings': total_listings,
        'pending_listings': pending_listings,
        'total_users': total_users,
        'total_bookings': total_bookings,
        'total_commission': total_commission,
        'monthly_commission': monthly_commission,
        'total_pending_payouts': total_pending_payouts,
        'expiring_soon': expiring_soon,
        'recent_bookings': recent_bookings,
        'pending_payouts': pending_payouts,
    }
    return render(request, 'admin/dashboard.html', context)