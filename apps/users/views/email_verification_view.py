# ⚙️ 자동 변환됨: drf_yasg → drf_spectacular
# ✅ 필요 시 Serializer를 명시해 request/response를 세부적으로 조정하세요.

from django.db import models
from django.utils import timezone

class EmailVerification(models.Model):
    email = models.EmailField(unique=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)

    def is_expired(self):
        return (timezone.now() - self.created_at).seconds > 300  # 5분 유효
