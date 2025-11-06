# apps/community/common.py
from typing import Sequence, Tuple, Optional, Dict, Any
from rest_framework.permissions import BasePermission, SAFE_METHODS
import base64
from rest_framework import serializers

# === 카테고리 ===
CATEGORY_ALL_KOR = "전체"
CATEGORY_KOR_ALLOWED = ["자유게시판", "정보공유", "질문게시판"]

def is_all_category(cat: Optional[str]) -> bool:
  return cat is None or cat == "" or cat == CATEGORY_ALL_KOR

def normalize_category_input(cat: Optional[str]) -> Optional[str]:
    if is_all_category(cat):
        return None
    return cat

def default_sort_for_category(_cat: Optional[str]) -> str:
    """현재 정책: '전체' 포함 모든 카테고리의 기본 정렬은 latest"""
    return "latest"

# === base64 ID ===
def id_to_public(id_int: int) -> str:
    return base64.urlsafe_b64encode(str(id_int).encode()).decode().rstrip("=")

def id_from_public(pub: str) -> int:
    pad = "=" * ((4 - len(pub) % 4) % 4)
    return int(base64.urlsafe_b64decode((pub + pad).encode()).decode())

class Base64IDField(serializers.Field):
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

# === 권한/도우미 ===
class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.is_staff or getattr(obj, "author_id", None) == user.id

def slice_with_has_next(items: Sequence, limit: int) -> Tuple[Sequence, bool]:
    has_next = len(items) > limit
    return items[:limit], has_next

# === 신고 사유 매핑/검증 ===
REASON_CODE_TO_LABEL = {
    "HATE":      "혐오 및 차별",
    "INSULT":    "욕설 및 비방",
    "ILLEGAL":   "불법 정보",
    "SPAM":      "스팸 및 홍보성 게시물",
    "PRIVACY":   "개인정보 침해",
    "COPYRIGHT": "저작권/지적재산권 침해",
    "YOUTH":     "청소년 유해 정보",
    "OTHER":     "기타",
}
REASON_LABEL_TO_CODE = {v: k for k, v in REASON_CODE_TO_LABEL.items()}

def reason_code_to_label(code: str) -> str:
    return REASON_CODE_TO_LABEL.get(code, "기타")

def reason_label_to_code(label: str) -> str:
    return REASON_LABEL_TO_CODE.get(label, "OTHER")

def validate_report(reason_code: str, detail: str) -> None:
    if reason_code == "OTHER" and len((detail or "").strip()) < 5:
        from django.core.exceptions import ValidationError
        raise ValidationError("기타 신고 사유는 상세 설명 5자 이상이 필요합니다.")

# === 프리뷰/좋아요(지연 임포트) ===
def preview_comments(post_id: int, limit: int = 3, after_id: Optional[int] = None) -> Dict[str, Any]:
    from apps.community.comments.models import Comment
    qs = Comment.objects.filter(post_id=post_id, is_deleted=False).order_by("-id")
    if after_id:
        qs = qs.filter(id__lt=after_id)

    rows = list(qs.select_related("author")[: limit + 1])
    page, has_next = slice_with_has_next(rows, limit)
    next_after = page[-1].id if has_next else None
    total = Comment.objects.filter(post_id=post_id, is_deleted=False).count()

    return {
        "items": [{
            "id": id_to_public(c.id),
            "author_id": c.author_id,
            "content": c.content,
            "created_at": c.created_at,
        } for c in page],
        "has_next": has_next,
        "next_after": id_to_public(next_after) if has_next and next_after else None,
        "total_count": total,
    }

def set_like(user_id: int, target, mode: str):
    from django.db import transaction
    from django.db.models import F
    from django.contrib.contenttypes.models import ContentType
    from apps.community.likes.models import Like
    with transaction.atomic():
        ct = ContentType.objects.get_for_model(target.__class__)
        oid = target.pk
        if mode == "ON":
            _, created = Like.objects.get_or_create(user_id=user_id, content_type=ct, object_id=oid)
            if created:
                target.__class__.objects.filter(id=target.id).update(like_count=F("like_count") + 1)
            is_liked = True
        else:
            deleted, _ = Like.objects.filter(user_id=user_id, content_type=ct, object_id=oid).delete()
            if deleted:
                target.__class__.objects.filter(id=target.id).update(like_count=F("like_count") - 1)
            is_liked = False
        current = target.__class__.objects.only("like_count").get(id=target.id).like_count
        return is_liked, current
