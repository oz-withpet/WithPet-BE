from rest_framework import serializers
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
        # 스펙 외 라벨은 400
        if label not in REASON_LABEL_TO_CODE:
            raise serializers.ValidationError({"reason": "지원하지 않는 신고 사유입니다."})
        code = reason_label_to_code(label)  # 한글 → 코드
        detail = (attrs.get("detail") or "").strip()
        validate_report(code, detail)       # 'OTHER'면 5자 이상 등 검증
        attrs["reason_code"] = code         # 뷰에서 저장 시 사용
        return attrs


class ReportCreatedOut(serializers.Serializer):
    # 스펙: report_id (외부 base64)
    report_id = Base64IDField()
