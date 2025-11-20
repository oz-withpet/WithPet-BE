from rest_framework_simplejwt.views import TokenObtainPairView


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        data = response.data
        access_token = data.get("access")
        refresh_token = data.get("refresh")

        # 반환할 Body는 access만 남기기
        response.data = {
            "access": access_token,
            "refresh": refresh_token
        }

        response.delete_cookie("access_token", path="/", domain='.withpet.space')
        response.delete_cookie("refresh_token", path="/", domain='.withpet.space')


        if access_token:
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="Lax",
                max_age=60 * 60,
                domain='.withpet.space',
            )

        if refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite="Lax",
                max_age=60 * 60 * 24 * 14,
                domain='.withpet.space',
            )

        return response

