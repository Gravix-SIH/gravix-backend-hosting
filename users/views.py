from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import timedelta

from .serializers import SignupSerializer, LoginSerializer, UserSerializer
from .models import User, VerificationToken
from gravix.utils import send_account_verification_code
import uuid


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    }

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            **tokens
        })


class SendVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        name = request.data.get('name')
        password = request.data.get('password')
        role = request.data.get('role', 'student')

        if not email or not name or not password:
            return Response(
                {'error': 'Email, name, and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if a verified user already exists — must login instead
        existing_verified = User.objects.filter(email=email, is_verified=True).exists()
        if existing_verified:
            return Response(
                {'error': 'An account with this email already exists. Please log in.'},
                status=status.HTTP_409_CONFLICT
            )

        # Check if unverified user exists — allow re-send of verification code
        existing_unverified = User.objects.filter(email=email, is_verified=False).exists()
        if existing_unverified:
            # Delete any existing pending tokens
            VerificationToken.objects.filter(email=email, used=False).delete()

            # Generate new code and send to the already-registered user
            raw_code = VerificationToken.generate_code()
            hashed_code = make_password(raw_code)
            # Get the user's current name from DB for the email
            user_obj = User.objects.get(email=email)
            display_name = user_obj.name or name

            token = VerificationToken.objects.create(
                email=email,
                code=hashed_code,
                name=display_name,
                password=password,  # Store raw; set_password() will hash it properly
                role=role,
                expires_at=timezone.now() + timedelta(minutes=10),
            )

            email_sent = send_account_verification_code(email, display_name, raw_code, expires_in_minutes=10)
            if not email_sent:
                token.delete()
                return Response(
                    {'error': 'Failed to send verification email. Please try again.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response({
                'success': True,
                'email': email,
            })

        # New user — create verification token and send code
        # Delete any existing pending tokens for this email
        VerificationToken.objects.filter(email=email, used=False).delete()

        # Generate 6-digit code
        raw_code = VerificationToken.generate_code()
        hashed_code = make_password(raw_code)

        # Create verification token with 10-minute expiry
        # Store raw password; set_password() will hash it properly during user creation
        token = VerificationToken.objects.create(
            email=email,
            code=hashed_code,
            name=name,
            password=password,
            role=role,
            expires_at=timezone.now() + timedelta(minutes=10),
        )

        # Send email
        email_sent = send_account_verification_code(email, name, raw_code, expires_in_minutes=10)

        if not email_sent:
            token.delete()
            return Response(
                {'error': 'Failed to send verification email. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            'success': True,
            'email': email,
        })


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response(
                {'error': 'Email and code are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find pending token
        try:
            token = VerificationToken.objects.get(email=email, used=False)
        except VerificationToken.DoesNotExist:
            return Response(
                {'error': 'No pending verification found. Please register again.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check expiry
        if token.is_expired():
            token.delete()
            return Response(
                {'error': 'Verification code has expired. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check code
        if not check_password(code, token.code):
            return Response(
                {'error': 'Invalid verification code'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark token as used
        token.used = True
        token.save()

        # Check if user already exists (registered but unverified)
        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            # Verify the existing user
            existing_user.is_verified = True
            existing_user.set_password(token.password)
            existing_user.save()
            user = existing_user
        else:
            # Create new user with is_verified=True
            user = User.objects.create(
                username=token.email,
                email=token.email,
                name=token.name,
                role=token.role,
                is_verified=True,
            )
            user.set_password(token.password)
            user.save()

        # Delete the token now that it's been used
        token.delete()

        # Return tokens
        tokens = get_tokens_for_user(user)
        return Response({
            'success': True,
            'user': UserSerializer(user).data,
            **tokens,
        })


class ResendVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find existing pending token
        try:
            token = VerificationToken.objects.get(email=email, used=False)
        except VerificationToken.DoesNotExist:
            return Response(
                {'error': 'No pending registration found. Please register again.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate new code
        raw_code = VerificationToken.generate_code()
        token.code = make_password(raw_code)
        token.expires_at = timezone.now() + timedelta(minutes=10)
        token.save()

        # Resend email
        email_sent = send_account_verification_code(email, token.name, raw_code, expires_in_minutes=10)

        if not email_sent:
            return Response(
                {'error': 'Failed to send verification email. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            'success': True,
            'email': email,
        })


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Enforce email verification for students; admins/counselors bypass this check
        if user.role == 'student' and not user.is_verified:
            return Response(
                {'error': 'Please verify your email address before logging in.'},
                status=status.HTTP_403_FORBIDDEN
            )

        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            **tokens
        })
    

class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserDetailView(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_object(self):
        obj = super().get_object()
        if self.request.user.role != 'admin' and obj.id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to access this user.")
        return obj

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        
        if 'role' in request.data and request.user.role != 'admin':
            return Response({"detail": "Only admin can update role"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response({"detail": "User deleted"}, status=status.HTTP_204_NO_CONTENT)


class AnonymousSessionView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        anon_id = f"anon_{uuid.uuid4().hex[:8]}"
        anon_user = User.objects.create(
            username=anon_id,
            email=f"{anon_id}@anonymous.temp",
            name="",
            is_anonymous=True,
            anon_id=anon_id,
            role=User.Role.STUDENT,
            is_active=True
        )
        
        refresh = RefreshToken.for_user(anon_user)
        refresh['role'] = anon_user.role
        refresh['is_anonymous'] = True
        
        return Response({
            'user': UserSerializer(anon_user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })

class RootStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({
            "status": "online",
            "message": "API is running",
        })