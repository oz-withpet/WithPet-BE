from django.contrib.auth import get_user_model
from django.db import IntegrityError
from typing import Dict, Any, Optional

from apps.users.utils.profanity_filter import contains_profanity
from apps.mypage.repository.user_repo import UserRepository

from apps.common.exceptions import (
    NicknameConflictError,
    InvalidPasswordError,
    UserNotFoundError,
    NicknameMismatchError,
)

User = get_user_model()

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_profile(self, user_id: int) -> Dict[str, Any]:
        # 프로필 정보 조회
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found.")

        return {
            "email": user.email,
            "nickname": user.nickname,
            "username": user.first_name,
            "gender": user.gender,
            "pet_type": user.pet_type,
            "is_email_verified": user.is_email_verified,
            "created_at": user.date_joined.isoformat(),
        }

    def update_profile(self, user_id: int, update_data: Dict[str, Any]) -> None:
        # 프로필 수정
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found.")

        nickname = update_data.get('nickname')

        if nickname:
            if contains_profanity(nickname):
                raise NicknameConflictError("닉네임에 부적절한 단어가 포함되어 있습니다.")

            if nickname != user.nickname:
                if not self.user_repo.is_nickname_unique(nickname, user_id):
                    raise NicknameConflictError("이미 사용 중인 닉네임입니다.")

        try:
            self.user_repo.update_profile(user, update_data)
        except IntegrityError:
            raise NicknameConflictError("프로필 업데이트 실패: 데이터 충돌")


    def check_nickname_availability(self, nickname: str) -> bool:
        # 닉네임 사용 가능 여부
        if contains_profanity(nickname):
            return False

        return not User.objects.filter(nickname=nickname).exists()


    def change_password(self, user_id: int, new_password: str, confirm_password: str) -> None:
        # 비밀번호 변경
        if new_password != confirm_password:
            raise InvalidPasswordError("새 비밀번호와 확인 비밀번호가 일치하지 않습니다.")

        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found.")

        user.set_password(new_password)
        user.save(update_fields=['password'])


    def withdraw_user(self, user_id: int, nickname_input: Optional[str]) -> None:
        # 회원 탈퇴
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found.")

        if not nickname_input or nickname_input != user.nickname:
            raise NicknameMismatchError("입력한 닉네임이 현재 사용자 닉네임과 일치하지 않습니다.")

        self.user_repo.deactivate_user(user)