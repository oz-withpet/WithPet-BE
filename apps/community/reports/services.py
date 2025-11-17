from django.core.exceptions import ValidationError as DjangoValidationError
from apps.community.common import id_from_path_param, validate_report, reason_label_to_code, REASON_LABEL_TO_CODE
from .repositories import ReportRepository
from .models import Report

def create_post_report(user, public_post_id: str, reason_label: str, detail: str) -> Report:

    try:
        post_pk = id_from_path_param(public_post_id)
    except Exception:
        raise ValueError("유효하지 않은 게시글 ID입니다.")

    if reason_label not in REASON_LABEL_TO_CODE:
        raise DjangoValidationError("지원하지 않는 신고 사유입니다.")

    reason_code = reason_label_to_code(reason_label)
    validate_report(reason_code, detail)

    post = ReportRepository.get_post_or_404(post_pk)

    report = ReportRepository.create_for_post(user=user, post=post, reason_code=reason_code, detail=detail)
    return report
