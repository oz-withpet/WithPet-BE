# apps/community/posts/services/detail.py

from __future__ import annotations

from typing import Optional, Dict
import binascii
import hashlib

from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound

from apps.community.posts.models import Post
from apps.community.posts.serializers import PostDetailOut, CommentsBlockOut
from apps.community.common import id_from_path_param, preview_comments


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


def _make_etag_detail(
    post: Post,
    include: Optional[str],
    limit: int,
    after_token: Optional[str],
    preview: Optional[Dict],
) -> str:
    try:
        updated_iso = post.updated_at.isoformat()
    except (AttributeError, ValueError, TypeError):
        updated_iso = str(post.updated_at)

    post_key = f"{post.id}:{updated_iso}:{post.view_count}:{post.like_count}:{post.comment_count}"

    comments_key = ""
    if include == "comments" and preview:
        items = preview.get("items") or []
        total_count = int(preview.get("total_count") or 0)
        next_after = preview.get("next_after") or ""
        last_item_id = items[-1]["id"] if items else ""
        comments_key = f"{total_count}:{next_after}:{last_item_id}"

    etag_src = f"detail:{post_key}:{include or ''}:{limit}:{after_token or ''}:{comments_key}"
    return f'W/"{hashlib.md5(etag_src.encode()).hexdigest()}"'


def _get_post_or_404(post_int_id: int) -> Post:
    post = (
        Post.objects.filter(id=post_int_id, is_deleted=False)
        .select_related("category", "author")
        .prefetch_related("images")
        .first()
    )
    if not post:
        raise NotFound(detail="게시글을 찾을 수 없습니다.")
    return post


def get_post_detail(request, post_id: str):
    # 👉 변경: 숫자("2") 또는 base64("Mg")를 모두 내부 정수 PK로 변환
    try:
        internal_id = id_from_path_param(post_id)
    except ValidationError as e:
        # 숫자/문자 모두 실패 시, 메시지를 사용자 친화적으로 유지
        raise ValidationError({"post_id": "유효하지 않은 ID입니다. 숫자 또는 base64 문자열을 사용하세요."}) from e

    post = _get_post_or_404(internal_id)

    include, limit, after = _parse_params(request.query_params)

    preview: Optional[Dict] = None
    if include == "comments":
        after_int: Optional[int] = None
        if after:
            # 댓글 프리뷰 커서는 기존 스펙대로 base64만 허용 (변경 없음)
            try:
                after_int = id_from_path_param(after)
            except (ValueError, TypeError, binascii.Error):
                raise ValidationError({"comments_after": "유효하지 않은 base64 ID입니다."})
        preview = preview_comments(post_id=post.id, limit=limit, after_id=after_int)

    etag_val = _make_etag_detail(post, include, limit, after, preview)

    # 조건부 요청 처리
    if request.META.get("HTTP_IF_NONE_MATCH") == etag_val:
        return Response(status=status.HTTP_304_NOT_MODIFIED)

    # 직렬화
    data: Dict = {"post": PostDetailOut(post, context={"request": request}).data}
    if include == "comments" and preview is not None:
        block = CommentsBlockOut(instance=preview, context={"request": request})
        data["comments"] = block.data

    resp = Response(data, status=status.HTTP_200_OK)
    resp["ETag"] = etag_val
    resp["Cache-Control"] = "public, max-age=60"
    return resp
