from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiRequest, OpenApiResponse, OpenApiExample
from rest_framework import serializers


# ✅ 요청 바디 정의용 Serializer
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(help_text="리프레시 토큰", required=True)


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="로그아웃 (JWT 블랙리스트)",
        description=(
            "사용자의 리프레시 토큰을 블랙리스트에 등록하여 로그아웃을 수행합니다.\n"
            "요청 시 refresh 토큰을 반드시 전달해야 합니다."
        ),
        request=LogoutSerializer,
        responses={
            200: OpenApiResponse(description="로그아웃 완료"),
            400: OpenApiResponse(description="잘못된 요청 또는 유효하지 않은 토큰"),
        },
        tags=["Users"],
        examples=[
            OpenApiExample(
                "정상 요청 예시",
                value={"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."},
                request_only=True,
            ),
            OpenApiExample(
                "성공 응답 예시",
                value={"detail": "로그아웃 완료"},
                response_only=True,
            ),
        ],
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "리프레시 토큰이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "로그아웃 완료"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "유효하지 않은 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST)

