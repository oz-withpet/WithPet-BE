from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from apps.users.serializers.login_serializer import LoginSerializer


class LoginAPIView(APIView):
    @extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                response=None,
                description="로그인 성공 — access, refresh 토큰 반환"
            ),
            400: OpenApiResponse(
                response=None,
                description="잘못된 요청 또는 인증 실패"
            ),
        },
        summary="로그인 API",
        description="사용자가 이메일과 비밀번호로 로그인하여 JWT 토큰을 발급받습니다.",
        tags=["Users"],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "message": f"{user.nickname}님, 환영합니다!"
            },
            status=status.HTTP_200_OK
        )

