# ⚙️ 자동 변환됨: drf_yasg → drf_spectacular
# ✅ 필요 시 Serializer를 명시해 request/response를 세부적으로 조정하세요.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework import serializers

class VerifyEmailCodeAPIView(APIView):
    """
    이메일 인증코드 검증 API
    ✅ 인증 성공 시 캐시에서 코드 삭제
    """
    permission_classes = [permissions.AllowAny]

    # 🔹 Swagger 요청 파라미터 정의
    @extend_schema(summary='API 설명을 추가하세요', responses={200: OpenApiResponse(description='성공')})
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
