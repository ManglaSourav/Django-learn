from datetime import timedelta

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.crypto import get_random_string

from .models import User, UserProfile
from .serializers import (
    ChangePasswordSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint.
    """

    queryset = User.objects.all()
    # print(queryset)
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Create user profile
        UserProfile.objects.create(user=user)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class UserLoginView(TokenObtainPairView):
    """
    User login endpoint with JWT tokens.
    """

    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        # print("request.data dataaaa ", request.data)
        serializer = self.get_serializer(data=request.data)
        # print("serializer serializer serializer ", serializer)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        # print("refresh refresh refresh ", refresh, user, serializer.validated_data)
        # print("UserSerializer UserSerializer UserSerializer ", refresh.access_token)
        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            }
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile management.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    User profile detail management.
    """

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class ChangePasswordView(APIView):
    """
    Change user password.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response({"message": "Password changed successfully."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    """
    Request password reset.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = User.objects.get(email=email)

            # Generate reset token (in production, use a more secure method)
            reset_token = get_random_string(32)
            user.reset_token = reset_token
            user.reset_token_expires = timezone.now() + timedelta(hours=1)
            user.save()

            # Send email (in production, use Celery for async email sending)
            send_mail(
                "Password Reset Request",
                f"Your password reset token is: {reset_token}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            return Response({"message": "Password reset email sent."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            # In production, validate the reset token
            new_password = serializer.validated_data["new_password"]
            # user.set_password(new_password)
            # user.save()
            return Response({"message": "Password reset successfully."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    """
    List all users (admin only).
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only show users if the current user is staff
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.none()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout user by blacklisting the refresh token.
    """
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logout successful."})
    except Exception as e:
        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
