from typing import Optional
from django.db import IntegrityError, transaction
from django.contrib.contenttypes.models import ContentType

from .repositories import get_post_or_404
from .serializers import ReportRequestIn

class DuplicateReportError(Exception):
    """동일 대상에 대한 중복 신고(409)"""
    pass

class ReportModelNotCompatible(Exception):
    """Report 모델이 post FK 또는 GFK(content_type, object_id) 구조가 아님"""
    pass

def _get_report_model():
    # 프로젝트의 Report 모델 경로 유지
    from apps.community.reports.models import Report
    return Report

def create_post_report(*, user, post_id: int, reason_label: str, detail: Optional[str]) -> int:
    """
    - post_id: base64 디코드된 정수
    - reason_label: 한글 라벨(Serializer에서 코드로 검증/변환)
    - 중복 신고 시 IntegrityError → DuplicateReportError로 승격
    - 정상 생성 시 생성된 report.pk 반환
    """
    # 1) 요청 유효성 검증
    ser = ReportRequestIn(data={"reason": reason_label, "detail": detail})
    ser.is_valid(raise_exception=True)
    reason_code = ser.validated_data["reason_code"]
    detail = ser.validated_data["detail"]

    # 2) 대상 Post 조회
    post = get_post_or_404(post_id)

    # 3) Report 저장 (FK or GFK 자동 호환)
    report_model = _get_report_model()  # ✅ 린터 대응: 소문자 변수명
    has_post_fk = hasattr(report_model, "post")
    has_gfk = hasattr(report_model, "content_type") and hasattr(report_model, "object_id")

    if not (has_post_fk or has_gfk):
        raise ReportModelNotCompatible(
            "Report 모델은 post FK 또는 (content_type, object_id) GFK 중 하나를 포함해야 합니다."
        )

    # 모델 필드 유무에 맞춰 안전하게 kwargs 구성
    kwargs = {
        "user": user,
        **({"reason_code": reason_code} if hasattr(report_model, "reason_code") else {}),
        **({"reason_label": reason_label} if hasattr(report_model, "reason_label") else {}),
        **({"detail": detail} if hasattr(report_model, "detail") else {}),
    }

    try:
        with transaction.atomic():
            if has_post_fk:
                # (A) post FK를 사용하는 모델
                kwargs["post"] = post
                obj = report_model.objects.create(**kwargs)
            else:
                # (B) GenericForeignKey(content_type, object_id) 사용하는 모델
                ct = ContentType.objects.get_for_model(post.__class__)
                kwargs["content_type"] = ct
                kwargs["object_id"] = post.pk
                obj = report_model.objects.create(**kwargs)
    except IntegrityError:
        # 유니크 제약 충돌 → 409
        raise DuplicateReportError()

    return obj.pk
