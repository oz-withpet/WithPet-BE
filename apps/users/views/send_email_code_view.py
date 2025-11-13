# ⚙️ 자동 변환됨: drf_yasg → drf_spectacular
# ✅ 필요 시 Serializer를 명시해 request/response를 세부적으로 조정하세요.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample
from apps.users.utils.email_service import send_verification_email

class SendEmailCodeAPIView(APIView):
    @extend_schema(
        summary="이메일 인증번호 전송",
        description="입력한 이메일 주소로 인증번호를 전송합니다.",
        request={"email": "string"},
        examples=[
            OpenApiExample(
                name="성공 예시",
                value={"message": "인증 코드가 이메일로 전송되었습니다."},
            ),
            OpenApiExample(
                name="실패 예시",
                value={"error": "이메일이 필요합니다."},
            ),
        ],
        responses={200: None, 400: None},
    )
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "이메일이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 이메일 전송 로직 호출
        send_verification_email(email)
        return Response({"message": "인증 코드가 이메일로 전송되었습니다."}, status=status.HTTP_200_OK)
