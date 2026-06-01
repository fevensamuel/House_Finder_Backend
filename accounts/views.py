from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate
from .models import User
from .serializers import RegisterSerializer, UserSerializer, ProfileUpdateSerializer
from rest_framework import status

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=400)

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Invalid credentials'}, status=400)

class MeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response(UserSerializer(request.user).data)
    
    def put(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile update requested, pending admin approval'})
        return Response(serializer.errors, status=400)

class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def put(self, request):
        if 'avatar' in request.FILES:
            request.user.avatar = request.FILES['avatar']
            request.user.save()
            return Response({'avatar': request.user.avatar.url if request.user.avatar else None})
        return Response({'error': 'No image provided'}, status=400)