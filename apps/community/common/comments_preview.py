# apps/community/common/comments_preview.py
from typing import Optional, Dict, Any, Sequence, Tuple
from django.db import models  # ✅ 타입: models.QuerySet (제네릭 미사용으로 호환성↑)
from apps.community.comments.models import Comment
from .id_codec import id_to_public


def _slice_with_has_next(items: Sequence, limit: int) -> Tuple[Sequence, bool]:
    has_next = len(items) > limit
    return items[:limit], has_next


def preview_comments(post_id: int, limit: int = 20, after_id: Optional[int] = None) -> Dict[str, Any]:
    """
    댓글 프리뷰: 최신순(id desc), 커서=마지막 id 기반. next_after는 base64 공개 ID로 반환.
    """
    # ✅ 제네릭 제거: 다양한 타입 체커(PyCharm/pyright/django-stubs)에서 경고 방지
    qs: models.QuerySet = Comment.objects.filter(post_id=post_id, is_deleted=False).order_by("-id")
    if after_id:
        qs = qs.filter(id__lt=after_id)

    rows = list(qs.select_related("author")[: limit + 1])
    page, has_next = _slice_with_has_next(rows, limit)
    next_after_int = page[-1].id if has_next else None
    total = Comment.objects.filter(post_id=post_id, is_deleted=False).count()

    def _author_dict(c: Comment) -> Dict[str, Any]:
        # 사용자 모델 스키마 차이를 흡수: nickname → username → email 순으로 표시
        nick = getattr(c.author, "nickname", None) or getattr(c.author, "username", None) or getattr(c.author, "email", "") or ""
        return {
            "user_id": c.author_id,  # 스펙 Author.user_id는 int64로 유지
            "nickname": nick,
        }

    return {
        "items": [
            {
                "id": id_to_public(c.id),  # base64 공개 ID
                "author": _author_dict(c),
                "content": c.content,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
                "is_deleted": c.is_deleted,
            }
            for c in page
        ],
        "total_count": total,
        "has_next": has_next,
        "next_after": id_to_public(next_after_int) if has_next and next_after_int else None,
    }
