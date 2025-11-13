from rest_framework.exceptions import APIException


class UserNotFoundError(APIException):
    # 사용자 찾을 수 없음
    status_code = 404
    default_detail = "사용자 정보를 찾을 수 없습니다."
    default_code = "USER_NOT_FOUND"


class NicknameConflictError(APIException):
    # 닉네임 중복 or 비속어
    status_code = 409
    default_detail = "닉네임이 이미 사용 중이거나 부적절합니다."
    default_code = "NICKNAME_CONFLICT"


class NicknameMismatchError(APIException):
    # 회원 탈퇴시 닉네임 확인
    status_code = 403
    default_detail = "입력된 닉네임이 현재 사용자의 닉네임과 일치하지 않습니다."
    default_code = "NICKNAME_MISMATCH"


class InvalidPasswordError(APIException):
    # 비밀번호 확인
    status_code = 403
    default_detail = "새 비밀번호가 일치하지 않거나 유효하지 않습니다."
    default_code = "INVALID_PASSWORD"


# 템플릿 사용을 위한 API 응답 래퍼런스
class ApiErrorWrapper:
    """API 에러 응답 포맷을 맞추기 위한 래퍼"""
    def __init__(self, code: str, message: str, details=None):
        self.code = code
        self.message = message
        self.details = details

    def to_dict(self):
        return {
            "success": False,
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details
            }
        }

class ApiSuccessWrapper:
    # API 응답 성공
    def __init__(self, data=None, message="성공적으로 처리되었습니다."):
        self.data = data
        self.message = message

    def to_dict(self):
        response = {"success": True}
        if self.message:
            response["message"] = self.message
        if self.data is not None:
            response["data"] = self.data
        return response