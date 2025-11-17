# apps/community/common/id_codec.py
import base64
from typing import Union
from rest_framework import serializers


def id_to_public(id_int: int) -> str:
    """
    내부 정수 PK -> urlsafe base64 문자열(패딩 '=' 제거)
    e.g. 2 -> "Mg"
    """
    return base64.urlsafe_b64encode(str(int(id_int)).encode()).decode().rstrip("=")


def id_from_public(pub: str) -> int:
    """
    urlsafe base64 문자열 -> 내부 정수 PK
    e.g. "Mg" -> 2
    """
    pad = "=" * ((4 - len(pub) % 4) % 4)
    return int(base64.urlsafe_b64decode((pub + pad).encode()).decode())


def id_from_path_param(value: Union[str, int]) -> int:
    """
    경로 파라미터(post_id 등)에서 받은 값을 내부 정수 PK로 변환.
    - 숫자 문자열("2") 또는 int(2)면 그대로 정수 반환
    - 그 외는 기존 규칙의 urlsafe base64로 디코딩 시도
    - 실패 시 DRF ValidationError 발생
    """
    # int 그대로 허용
    if isinstance(value, int):
        return value

    # 문자열 처리
    s = (value or "").strip()
    if s.isdigit():               # 숫자 URL 지원: "/posts/2"
        return int(s)

    # base64(urlsafe, padding 보정) 시도: "/posts/Mg"
    try:
        pad = "=" * ((4 - len(s) % 4) % 4)
        return int(base64.urlsafe_b64decode((s + pad).encode()).decode())
    except Exception:
        raise serializers.ValidationError(
            {"post_id": "유효하지 않은 ID입니다. 숫자 또는 base64 문자열을 사용하세요."}
        )


class Base64IDField(serializers.Field):
    """
    Serializer에서 내부 int PK를 base64 문자열로 입출력 변환
    (응답은 계속 base64로 내보냄 — 기존 스펙 유지)
    """
    def to_representation(self, value):
        pk = int(value.pk if hasattr(value, "pk") else value)
        return id_to_public(pk)

    def to_internal_value(self, data):
        if not isinstance(data, str):
            raise serializers.ValidationError("ID는 base64 문자열이어야 합니다.")
        try:
            return id_from_public(data)
        except Exception:
            raise serializers.ValidationError("유효하지 않은 base64 ID입니다.")
