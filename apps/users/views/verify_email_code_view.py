from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class VerifyEmailCodeAPIView(APIView):
    """
    이메일 인증코드 검증 API
    ✅ 인증 성공 시 캐시에서 코드 삭제
    """
    permission_classes = [permissions.AllowAny]

    # 🔹 Swagger 요청 파라미터 정의
    @swagger_auto_schema(
        operation_summary="이메일 인증코드 검증",
        operation_description="사용자가 입력한 이메일과 인증코드를 검증합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "verification_code"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="사용자 이메일 주소"),
                "verification_code": openapi.Schema(type=openapi.TYPE_STRING, description="이메일로 발송된 인증코드"),
            },
        ),
        responses={
            200: openapi.Response(description="이메일 인증이 완료되었습니다."),
            400: openapi.Response(description="잘못된 요청 또는 인증 실패"),
        },
    )
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("verification_code")

        if not email or not code:
            return Response(
                {"detail": "이메일과 인증코드를 모두 입력해주세요."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cached_code = cache.get(email)
        if cached_code is None:
            return Response(
                {"detail": "인증코드가 만료되었거나 존재하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if cached_code != code:
            return Response(
                {"detail": "인증코드가 올바르지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ 인증 성공 시 캐시에서 코드 삭제
        cache.delete(email)

        return Response(
            {"detail": "이메일 인증이 완료되었습니다."},
            status=status.HTTP_200_OK
        )
