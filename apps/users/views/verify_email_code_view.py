# ⚙️ 자동 변환됨: drf_yasg → drf_spectacular
# ✅ 필요 시 Serializer를 명시해 request/response를 세부적으로 조정하세요.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample
from apps.users.utils.email_service import verify_email_code

class VerifyEmailCodeAPIView(APIView):
    @extend_schema(
        summary="이메일 인증번호 검증",
        description="이메일과 인증번호를 입력받아 유효한지 확인합니다.",
        request={"email": "string", "code": "string"},
        examples=[
            OpenApiExample(
                name="성공 예시",
                value={"verified": True, "message": "이메일 인증이 완료되었습니다."},
            ),
            OpenApiExample(
                name="실패 예시",
                value={"verified": False, "message": "인증번호가 일치하지 않습니다."},
            ),
        ],
        responses={200: None, 400: None},
    )
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return Response({"error": "이메일과 인증번호가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        verified = verify_email_code(email, code)
        if verified:
            return Response({"verified": True, "message": "이메일 인증이 완료되었습니다."})
        return Response({"verified": False, "message": "인증번호가 일치하지 않습니다."})

