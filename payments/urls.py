from django.urls import path
from .views import InitiatePaymentView, VerifyPaymentView

urlpatterns = [
    path('payments/initiate/', InitiatePaymentView.as_view()),
    path('payments/verify/<str:tx_ref>/', VerifyPaymentView.as_view()),
]