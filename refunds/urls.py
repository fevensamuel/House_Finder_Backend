from django.urls import path
from .views import CreateRefundRequestView, MyRefundRequestsView, LandlordRefundRequestsView

urlpatterns = [
    path('refunds/', CreateRefundRequestView.as_view()),
    path('refunds/my/', MyRefundRequestsView.as_view()),
    path('refunds/landlord/', LandlordRefundRequestsView.as_view()),
]