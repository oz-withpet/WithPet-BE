from django.urls import path
from apps.users.views.signup_view import SignupAPIView
from apps.users.views.token_obtain_view import CustomTokenObtainPairView
from apps.users.views.logout_view import LogoutAPIView
from apps.users.views.token_refresh_view import CustomTokenRefreshView
from apps.users.views.nickname_check_view import NicknameCheckAPIView
from apps.users.views.email_check_view import EmailCheckAPIView

urlpatterns = [
    # 🔐 인증 관련
    path("auth/signup/", SignupAPIView.as_view(), name="auth-signup"),
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutAPIView.as_view(), name="auth-logout"),
    path("auth/token/refresh/", CustomTokenRefreshView.as_view(), name="auth-token-refresh"),

    # ✅ 검증 관련
    path("validation/nickname/", NicknameCheckAPIView.as_view(), name="validation-nickname"),
    path("validation/email/", EmailCheckAPIView.as_view(), name="validation-email")
]
