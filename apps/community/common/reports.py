from typing import Dict

REASON_CODE_TO_LABEL: Dict[str, str] = {
    "HATE":      "혐오 및 차별",
    "INSULT":    "욕설 및 비방",
    "ILLEGAL":   "불법 정보",
    "SPAM":      "스팸 및 홍보성 게시물",
    "PRIVACY":   "개인정보 침해",
    "COPYRIGHT": "저작권/지적재산권 침해",
    "YOUTH":     "청소년 유해 정보",
    "OTHER":     "기타",
}
REASON_LABEL_TO_CODE: Dict[str, str] = {v: k for k, v in REASON_CODE_TO_LABEL.items()}

def reason_code_to_label(code: str) -> str:
    return REASON_CODE_TO_LABEL.get(code, "기타")

def reason_label_to_code(label: str) -> str:
    return REASON_LABEL_TO_CODE.get(label, "OTHER")

def validate_report(reason_code: str, detail: str) -> None:
    if reason_code == "OTHER" and len((detail or "").strip()) < 5:
        from django.core.exceptions import ValidationError
        raise ValidationError("기타 신고 사유는 상세 설명 5자 이상이 필요합니다.")
