from django.contrib.auth import get_user_model
from django.db import IntegrityError
from typing import Optional, Dict
from apps.users.models import CustomUser as User

class UserRepository:

  def get_user_by_id(self, user_id: int) -> Optional[User]:
    try:
      return User.objects.get(pk=user_id)
    except User.DoesNotExist:
      return None

  def update_profile(self, user: User, data: Dict[str, str]) -> User:
    for field, value in data.items():
      setattr(user, field, value)

    try:
      user.save(update_fields=list(data.keys()))
    except IntegrityError as e:
      raise IntegrityError("프로필 업데이트 중 오류 발생.") from e
    return user

  def is_nickname_unique(self, nickname: str, current_user_id: int) -> bool:
    # 현재 사용자를 제외 한 닉네임 중복 검사
    return not User.objects.exclude(pk=current_user_id).filter(nickname=nickname).exists()

  def deactivate_user(self, user: User) -> None:
    # 사용자 정보 비활성화
    user.is_active = False
    user.save(update_fields=['is_active'])