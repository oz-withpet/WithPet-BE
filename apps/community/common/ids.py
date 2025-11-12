# apps/common/ids.py
import base64

class InvalidId64Error(ValueError):
    pass

def decode_id64(id64: str) -> int:
    """
    Option B: base64로 인코딩된 '정수 문자열'을 디코드하여 int 반환.
    예: "123" -> base64 => "MTIz"  -> decode_id64("MTIz") == 123
    """
    try:
        raw = base64.b64decode(id64).decode("utf-8").strip()
        if not raw.isdigit():
            raise InvalidId64Error("decoded value is not a digit string")
        return int(raw)
    except Exception as e:
        raise InvalidId64Error(f"invalid base64 id: {e}")

def encode_id64(num: int) -> str:
    raw = str(int(num)).encode("utf-8")
    return base64.b64encode(raw).decode("utf-8")
