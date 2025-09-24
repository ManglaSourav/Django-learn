from rest_framework_simplejwt.views import TokenRefreshView

from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    # Authentication
    path("register/", views.UserRegistrationView.as_view(), name="register"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # User management
    path("profile/", views.UserProfileView.as_view(), name="profile"),
    path(
        "profile/detail/", views.UserProfileDetailView.as_view(), name="profile-detail"
    ),
    path(
        "change-password/", views.ChangePasswordView.as_view(), name="change-password"
    ),
    path("password-reset/", views.PasswordResetView.as_view(), name="password-reset"),
    path(
        "password-reset-confirm/",
        views.PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("users/", views.UserListView.as_view(), name="user-list"),
]
