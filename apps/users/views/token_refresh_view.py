# ⚙️ 자동 변환됨: drf_yasg → drf_spectacular
# ✅ 필요 시 Serializer를 명시해 request/response를 세부적으로 조정하세요.

from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.response import Response
from rest_framework import status

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"detail": "No refresh token in cookies"}, status=status.HTTP_400_BAD_REQUEST)

        request.data["refresh"] = refresh_token
        return super().post(request, *args, **kwargs)

