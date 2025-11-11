# apps/community/common/comments_preview.py
from typing import Optional, Dict, Any, Sequence, Tuple
from django.db import models
from apps.community.comments.models import Comment
from .id_codec import id_to_public

def _slice_with_has_next(items: Sequence, limit: int) -> Tuple[Sequence, bool]:
    has_next = len(items) > limit
    return items[:limit], has_next

def preview_comments(post_id: int, limit: int = 20, after_id: Optional[int] = None) -> Dict[str, Any]:
    """
    댓글 프리뷰: 최신순(id desc), 커서=마지막 id 기반.
    반환값의 items는 Comment 모델 인스턴스 리스트(Serializer가 처리).
    """
    qs: models.QuerySet = Comment.objects.filter(post_id=post_id, is_deleted=False).order_by("-id")
    if after_id:
        qs = qs.filter(id__lt=after_id)

    rows = list(qs.select_related("author")[: limit + 1])
    page, has_next = _slice_with_has_next(rows, limit)
    next_after_int = page[-1].id if has_next else None
    total = Comment.objects.filter(post_id=post_id, is_deleted=False).count()

    return {
        "items": page,  # ← 모델 인스턴스들
        "total_count": total,
        "has_next": has_next,
        "next_after": id_to_public(next_after_int) if has_next and next_after_int else None,
    }
