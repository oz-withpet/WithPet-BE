from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        data = response.data

        refresh_token = data.get("refresh")
        access_token = data.get("access")

        # refresh_token은 쿠키에 저장
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,  # JavaScript에서 접근 불가
            secure=False,   # HTTPS 환경에서는 True로 바꿔야 함
            samesite="Lax", # CSRF 방어 옵션
            max_age=7 * 24 * 60 * 60  # 7일
        )

        # body에는 refresh 제거 (보안상 이유)
        response.data = {"access": access_token}

        return response
