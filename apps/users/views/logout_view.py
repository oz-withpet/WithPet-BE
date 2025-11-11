# apps/users/views/logout_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="로그아웃 (JWT 블랙리스트)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='리프레시 토큰'),
            },
            required=['refresh']
        ),
        responses={
            200: '로그아웃 완료',
            400: '잘못된 요청',
        }
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "리프레시 토큰이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # 블랙리스트에 등록
            return Response({"detail": "로그아웃 완료"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "유효하지 않은 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST)
