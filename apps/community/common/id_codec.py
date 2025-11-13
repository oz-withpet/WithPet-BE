# apps/community/common/id_codec.py
import base64
from rest_framework import serializers


def id_to_public(id_int: int) -> str:
    """정수 PK → urlsafe base64 문자열(패딩 '=' 제거)"""
    return base64.urlsafe_b64encode(str(int(id_int)).encode()).decode().rstrip("=")


def id_from_public(pub: str) -> int:
    """urlsafe base64 문자열 → 정수 PK"""
    pad = "=" * ((4 - len(pub) % 4) % 4)
    return int(base64.urlsafe_b64decode((pub + pad).encode()).decode())


class Base64IDField(serializers.Field):
    """Serializer에서 내부 int PK를 base64 문자열로 입출력 변환"""
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
