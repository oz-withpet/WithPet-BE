from django.urls import path
from apps.users.views.signup_view import SignupAPIView
from apps.users.views.login_view import LoginAPIView
from apps.users.views.nickname_check_view import NicknameCheckAPIView
from apps.users.views.send_email_code_view import SendEmailCodeAPIView
from apps.users.views.verify_email_code_view import VerifyEmailCodeAPIView

urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('nickname-check/', NicknameCheckAPIView.as_view(), name='nickname_check'),
    path('send-email-code/', SendEmailCodeAPIView.as_view(), name='send_email_code'),
    path('verify-email-code/', VerifyEmailCodeAPIView.as_view(), name='verify_email_code'),
]
