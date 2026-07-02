# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate
from .models import User
from .serializers import RegisterSerializer, UserSerializer, ProfileUpdateSerializer

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

# accounts/views.py
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        # ✅ partial=True allows sending only the fields you want to update
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Return the updated user data
            return Response(UserSerializer(request.user).data)
        return Response(serializer.errors, status=400)

class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):
        if 'avatar' not in request.FILES:
            return Response({'error': 'No image provided'}, status=400)
        request.user.avatar = request.FILES['avatar']
        request.user.save()
        # ✅ Return absolute URL
        url = request.build_absolute_uri(request.user.avatar.url)
        return Response({'avatar': url})

class UploadIDDocumentView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):
        side = request.data.get('side')
        if side not in ['front', 'back']:
            return Response({'error': 'side must be "front" or "back"'}, status=400)

        if 'id_document' not in request.FILES:
            return Response({'error': 'No image provided'}, status=400)

        file = request.FILES['id_document']
        if side == 'front':
            request.user.id_front = file
        else:
            request.user.id_back = file
        request.user.save()

        url_field = request.user.id_front if side == 'front' else request.user.id_back
        if not url_field:
            return Response({'error': 'Failed to save image'}, status=500)

        url = request.build_absolute_uri(url_field.url)
        return Response({f'id_{side}': url})

class UpdateFCMTokenView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        token = request.data.get('fcm_token')
        if token:
            request.user.fcm_token = token
            request.user.save()
            return Response({'status': 'token saved'})
        return Response({'error': 'token required'}, status=400)