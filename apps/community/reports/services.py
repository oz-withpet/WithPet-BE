# apps/community/reports/services.py
from django.core.exceptions import ValidationError as DjangoValidationError
from apps.community.common import id_from_public, validate_report, reason_label_to_code, REASON_LABEL_TO_CODE
from .repositories import ReportRepository
from .models import Report

def create_post_report(user, public_post_id: str, reason_label: str, detail: str) -> Report:
    """
    신고 생성(포스트만 대상).
    - user: 인증 사용자 (필수)
    - public_post_id: urlsafe base64 공개 ID
    - reason_label: 한글 라벨(스펙 열거값)
    - detail: 기타일 때 5자 이상 필요
    """
    # 1) 공개 ID → 내부 int
    try:
        post_pk = id_from_public(public_post_id)
    except Exception:
        # 공개 ID 형식 불일치
        raise ValueError("유효하지 않은 게시글 ID입니다.")

    # 2) 라벨 → 코드, 검증
    if reason_label not in REASON_LABEL_TO_CODE:
        raise DjangoValidationError("지원하지 않는 신고 사유입니다.")

    reason_code = reason_label_to_code(reason_label)
    validate_report(reason_code, detail)

    # 3) 대상 조회
    post = ReportRepository.get_post_or_404(post_pk)

    # 4) 생성(중복은 DuplicateReportError)
    report = ReportRepository.create_for_post(user=user, post=post, reason_code=reason_code, detail=detail)
    return report
