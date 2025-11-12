# apps/community/reports/serializers.py
from rest_framework import serializers
from apps.community.common import (
    Base64IDField,
    reason_label_to_code,
    validate_report,
    REASON_LABEL_TO_CODE,
)

class ReportRequestIn(serializers.Serializer):
    """
    요청 바디 검증:
      - reason: 한글 라벨(스펙 라벨만 허용)
      - detail: 선택(단, '기타'일 때 validate_report에서 5자 이상 검증)
    유효성 통과 시 serializer.validated_data['reason_code'] 주입
    """
    reason = serializers.CharField()
    detail = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):
        label = (attrs.get("reason") or "").strip()
        if label not in REASON_LABEL_TO_CODE:
            raise serializers.ValidationError({"reason": "지원하지 않는 신고 사유입니다."})

        code = reason_label_to_code(label)           # 한글 → 내부 코드
        detail = (attrs.get("detail") or "").strip()
        validate_report(code, detail)                # 'OTHER'면 5자 이상 등 공통 검증

        attrs["reason_code"] = code                  # services에서 저장 시 사용
        attrs["detail"] = detail or None             # 빈 문자열 -> None 정규화
        return attrs


class ReportCreatedOut(serializers.Serializer):
    """
    응답 바디:
      - report_id: base64로 인코딩된 외부 노출 ID (Option B)
    """
    report_id = Base64IDField()