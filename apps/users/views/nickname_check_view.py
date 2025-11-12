# ⚙️ 자동 변환됨: drf_yasg → drf_spectacular
# ✅ 필요 시 Serializer를 명시해 request/response를 세부적으로 조정하세요.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.users.models import CustomUser


class NicknameCheckAPIView(APIView):
    def get(self, request):
        nickname = request.GET.get("nickname")
        if not nickname:
            return Response({"error": "닉네임이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        exists = CustomUser.objects.filter(nickname=nickname).exists()
        if exists:
            return Response({"available": False, "message": "이미 사용 중인 닉네임입니다."})
        return Response({"available": True, "message": "사용 가능한 닉네임입니다."})
