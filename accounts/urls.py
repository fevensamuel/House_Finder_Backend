from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (RegisterView, LoginView, MeView, AvatarUploadView,
                    UploadIDDocumentView, UpdateFCMTokenView)

urlpatterns = [
    path('auth/register/', RegisterView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('auth/me/', MeView.as_view()),
    path('auth/avatar/', AvatarUploadView.as_view()),
    path('auth/id-document/', UploadIDDocumentView.as_view()),
    path('auth/fcm-token/', UpdateFCMTokenView.as_view()),
]