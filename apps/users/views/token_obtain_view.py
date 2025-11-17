from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        data = response.data
        access_token = data.get("access")
        refresh_token = data.get("refresh")

        # 반환할 Body는 access만 남기기
        response.data = {
            "access": access_token
        }

        if access_token:
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="None",
                max_age=60 * 60,
            )

        if refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite="None",
                max_age=60 * 60 * 24 * 14,
            )

        return response

