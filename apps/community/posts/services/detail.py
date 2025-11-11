# apps/community/posts/services/detail.py
from typing import Optional
from django.db import models
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
    try:
        limit = int(qp.get("comments_limit", "20"))
    except ValueError:
        raise ValidationError({"comments_limit": "정수여야 합니다."})
    if not (1 <= limit <= 100):
        raise ValidationError({"comments_limit": "1~100 범위여야 합니다."})
    after = qp.get("comments_after")
    return include, limit, after

def get_post_detail(request, post_id: str):
    try:
        internal_id = id_from_public(post_id)
    except Exception:
        raise ValidationError({"post_id": "유효하지 않은 base64 ID입니다."})

    qs: models.QuerySet = Post.objects.select_related("category", "author").filter(is_deleted=False)
    post = get_object_or_404(qs, id=internal_id)

    include, limit, after = _parse_params(request.query_params)

    # 본문
    data = {"post": PostDetailOut(post, context={"request": request}).data}

    # 댓글 프리뷰
    if include == "comments":
        after_int = None
        if after:
            try:
                after_int = id_from_public(after)
            except Exception:
                raise ValidationError({"comments_after": "유효하지 않은 base64 ID입니다."})

        preview = preview_comments(post_id=post.id, limit=limit, after_id=after_int)
        # ✅ instance 모드로 직렬화 (items가 모델 인스턴스이므로 read_only 필드 충돌 없음)
        block = CommentsBlockOut(instance=preview, context={"request": request})
        data["comments"] = block.data

    return Response(data, status=status.HTTP_200_OK)
