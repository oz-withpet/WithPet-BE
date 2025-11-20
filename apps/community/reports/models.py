from __future__ import annotations

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from apps.community.common import validate_report, reason_code_to_label


class ReportReason(models.TextChoices):
    HATE      = "HATE",      "혐오 및 차별"
    INSULT    = "INSULT",    "욕설 및 비방"
    ILLEGAL   = "ILLEGAL",   "불법 정보"
    SPAM      = "SPAM",      "스팸 및 홍보성 게시물"
    PRIVACY   = "PRIVACY",   "개인정보 침해"
    COPYRIGHT = "COPYRIGHT", "저작권/지적재산권 침해"
    YOUTH     = "YOUTH",     "청소년 유해 정보"
    OTHER     = "OTHER",     "기타"


class ReportStatus(models.TextChoices):
    PENDING   = "PENDING",   "접수"
    RESOLVED  = "RESOLVED",  "처리완료"
    REJECTED  = "REJECTED",  "기각"


REPORT_REASON_CHOICES: tuple[tuple[str, str], ...] = (
    ("HATE", "혐오 및 차별"),
    ("INSULT", "욕설 및 비방"),
    ("ILLEGAL", "불법 정보"),
    ("SPAM", "스팸 및 홍보성 게시물"),
    ("PRIVACY", "개인정보 침해"),
    ("COPYRIGHT", "저작권/지적재산권 침해"),
    ("YOUTH", "청소년 유해 정보"),
    ("OTHER", "기타"),
)

REPORT_STATUS_CHOICES: tuple[tuple[str, str], ...] = (
    ("PENDING", "접수"),
    ("RESOLVED", "처리완료"),
    ("REJECTED", "기각"),
)


class Report(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reports",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, db_index=True)
    object_id = models.PositiveBigIntegerField(db_index=True)
    target = GenericForeignKey("content_type", "object_id")

    reason = models.CharField(max_length=20, choices=REPORT_REASON_CHOICES)
    detail = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=REPORT_STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "report"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"],
                name="uniq_user_target_report",
            )
        ]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def clean(self):
        validate_report(self.reason, self.detail)

    @property
    def reason_label(self) -> str:
        return reason_code_to_label(self.reason)
