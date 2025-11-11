from django.db import models
from django.utils import timezone

class EmailVerification(models.Model):
    email = models.EmailField(unique=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)

    def is_expired(self):
        return (timezone.now() - self.created_at).seconds > 300  # 5분 유효
