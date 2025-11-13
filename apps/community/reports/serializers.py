# apps/community/reports/serializers.py
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from apps.community.common import (
    Base64IDField,
    reason_label_to_code,
    validate_report,
    REASON_LABEL_TO_CODE,
)

class ReportRequestIn(serializers.Serializer):
    # 클라이언트는 한글 사유로 보냄 → 내부 코드로 변환
    reason = serializers.CharField()
    detail = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):
        label = (attrs.get("reason") or "").strip()
        if label not in REASON_LABEL_TO_CODE:
            # 스펙 외 라벨은 400
            raise serializers.ValidationError({"reason": "지원하지 않는 신고 사유입니다."})

        code = reason_label_to_code(label)  # 한글 → 코드
        detail = (attrs.get("detail") or "").strip()

        # 공통 검증(OTHER면 5자↑)
        try:
            validate_report(code, detail)
        except DjangoValidationError as e:
            msg = getattr(e, "message", None) or getattr(e, "messages", [None])[0] or str(e)
            raise serializers.ValidationError({"detail": msg})

        attrs["reason_code"] = code  # 저장용
        attrs["detail"] = detail
        return attrs


class ReportCreatedOut(serializers.Serializer):
    # 스펙: report_id는 공개 base64
    report_id = Base64IDField()
