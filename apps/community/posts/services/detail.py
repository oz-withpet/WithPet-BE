from typing import Optional
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
    # base64 → int
    try:
        internal_id = id_from_public(post_id)
    except Exception:
        raise ValidationError({"post_id": "유효하지 않은 base64 ID입니다."})

    # ✅ 모델 클래스 사용 → 타입 경고 제거
    post = get_object_or_404(Post, id=internal_id, is_deleted=False)

    # select_related가 필요하면, 아래 한 줄로 ‘다시 조회’(미세한 2nd 쿼리)
    post = Post.objects.select_related("category", "author").get(id=post.id)

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
        block = CommentsBlockOut(instance=preview, context={"request": request})
        data["comments"] = block.data

    return Response(data, status=status.HTTP_200_OK)
