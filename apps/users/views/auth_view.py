# ⚙️ 자동 변환됨: drf_yasg → drf_spectacular
# ✅ 필요 시 Serializer를 명시해 request/response를 세부적으로 조정하세요.

from rest_framework import generics, permissions
from apps.users.serializers.user_serializers import UserSerializer
from apps.users.models import User

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
