from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.cache import cache
from apps.users.utils.email_service import send_verification_email

class SendEmailCodeAPIView(APIView):
    """
    이메일 인증코드 발송 API
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'detail': '이메일을 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        # 이메일 인증코드 전송
        verification_code = send_verification_email(email)
        cache.set(f"email_verification:{email}", verification_code, timeout=300)  # 5분 유효

        return Response({'detail': '인증 코드가 이메일로 전송되었습니다.'}, status=status.HTTP_200_OK)
