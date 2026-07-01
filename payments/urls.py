from django.urls import path
from .views import (
    InitiatePaymentView, VerifyPaymentView,
    InitiateFeaturedPaymentView,
    AdminStatsView, MarkPayoutSentView
)

urlpatterns = [
    path('payments/initiate/', InitiatePaymentView.as_view()),
    path('payments/verify/<str:tx_ref>/', VerifyPaymentView.as_view()),
    path('featured/initiate/', InitiateFeaturedPaymentView.as_view()),
    path('admin/stats/', AdminStatsView.as_view()),
    path('admin/payouts/<int:payout_id>/mark-sent/', MarkPayoutSentView.as_view()),
]