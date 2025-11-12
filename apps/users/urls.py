from django.urls import path
from apps.users.views.signup_view import SignupAPIView
from apps.users.views.login_view import LoginAPIView
from apps.users.views.logout_view import LogoutAPIView
from apps.users.views.nickname_check_view import NicknameCheckAPIView
from apps.users.views.email_check_view import EmailCheckAPIView
from apps.users.views.send_email_code_view import SendEmailCodeAPIView
from apps.users.views.verify_email_code_view import VerifyEmailCodeAPIView
from apps.users.views.token_refresh_view import CustomTokenRefreshView

urlpatterns = [
    # 인증 관련
    path("auth/signup/", SignupAPIView.as_view(), name="auth-signup"),
    path("auth/login/", LoginAPIView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutAPIView.as_view(), name="auth-logout"),
    path("auth/token/refresh/", CustomTokenRefreshView.as_view(), name="auth-token-refresh"),

    # 검증 관련
    path("validation/nickname/", NicknameCheckAPIView.as_view(), name="validation-nickname"),
    path("validation/email/", EmailCheckAPIView.as_view(), name="validation-email"),

    # 이메일 인증 관련
    path("email/code/send/", SendEmailCodeAPIView.as_view(), name="email-code-send"),
    path("email/code/verify/", VerifyEmailCodeAPIView.as_view(), name="email-code-verify"),
]
