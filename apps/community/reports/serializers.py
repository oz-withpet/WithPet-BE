from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from apps.community.common import (
    reason_label_to_code,
    validate_report,
    REASON_LABEL_TO_CODE,
)


class ReportRequestIn(serializers.Serializer):
    reason = serializers.CharField()
    detail = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):
        label = (attrs.get("reason") or "").strip()
        if label not in REASON_LABEL_TO_CODE:
            raise serializers.ValidationError({"reason": "지원하지 않는 신고 사유입니다."})

        # 한글 라벨 → 내부 코드
        code = reason_label_to_code(label)
        detail = (attrs.get("detail") or "").strip()

        try:
            validate_report(code, detail)
        except DjangoValidationError as e:
            msg = (
                getattr(e, "message", None)
                or getattr(e, "messages", [None])[0]
                or str(e)
            )
            raise serializers.ValidationError({"detail": msg})

        attrs["reason_code"] = code  # 저장용 코드
        attrs["detail"] = detail     # 정제된 detail
        return attrs


class ReportCreatedOut(serializers.Serializer):
    report_id = serializers.IntegerField(read_only=True)
