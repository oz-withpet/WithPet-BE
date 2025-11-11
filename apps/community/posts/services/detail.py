# apps/community/posts/services/detail.py
from typing import Optional
from django.db import models  # ✅ 비제네릭 QuerySet 주석용
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from apps.community.posts.models import Post
from apps.community.posts.serializers import PostDetailOut, CommentsBlockOut
from apps.community.common import id_from_public, preview_comments


def _parse_params(qp) -> tuple[Optional[str], int, Optional[str]]:
    include = qp.get("include")
    if include not in (None, "comments"):
        raise ValidationError({"include": "허용된 값: comments"})

    raw_limit = qp.get("comments_limit", "20")
    try:
        limit = int(raw_limit)
    except ValueError:
        raise ValidationError({"comments_limit": "정수여야 합니다."})
    if not (1 <= limit <= 100):
        raise ValidationError({"comments_limit": "1~100 범위여야 합니다."})

    after = qp.get("comments_after")
    return include, limit, after


def get_post_detail(request, post_id: str):
    """
    GET /posts/{id}?include=comments&comments_limit&comments_after
    - id: base64 공개 ID → 내부 int
    - include=comments면 프리뷰 블록 포함
    """
    include, limit, after = _parse_params(request.query_params)

    # base64 → int
    try:
        internal_id = id_from_public(post_id)
    except Exception:
        raise ValidationError({"post_id": "유효하지 않은 base64 ID입니다."})

    # ✅ 타입 경고 제거: models.QuerySet(비제네릭)로 주석
    qs: models.QuerySet = (
        Post.objects.select_related("category", "author").filter(is_deleted=False)
    )
    post = get_object_or_404(qs, id=internal_id)

    # 본문 직렬화
    post_data = PostDetailOut(post, context={"request": request}).data
    data = {"post": post_data}

    # 댓글 프리뷰
    if include == "comments":
        after_int = None
        if after:
            try:
                after_int = id_from_public(after)
            except Exception:
                raise ValidationError({"comments_after": "유효하지 않은 base64 ID입니다."})

        preview = preview_comments(post_id=post.id, limit=limit, after_id=after_int)
        block = CommentsBlockOut(data=preview)
        block.is_valid(raise_exception=True)
        data["comments"] = block.data

    return Response(data, status=status.HTTP_200_OK)
