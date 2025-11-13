from __future__ import annotations

from typing import Optional

from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    NotFound,
    PermissionDenied,
    ValidationError,
    UnsupportedMediaType,
)

from apps.community.common import id_from_public, CATEGORY_KOR_ALLOWED
from apps.community.posts.models import Post, PostCategory


def _alive_qs():
    """살아있는(Post.is_deleted=False) 글만 조회하는 쿼리셋."""
    try:
        return Post.objects.alive()  # 커스텀 매니저가 있으면 사용
    except AttributeError:
        return Post.objects.filter(is_deleted=False)


def _parse_bool(val: object) -> Optional[bool]:
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        s = val.strip().lower()
        if s in {"true", "1", "yes", "y"}:
            return True
        if s in {"false", "0", "no", "n"}:
            return False
    raise ValidationError({"image_delete": "boolean 형식이어야 합니다."})


def _ensure_author_or_403(request_user, post: Post) -> None:
    if not getattr(request_user, "is_authenticated", False):
        raise PermissionDenied("로그인이 필요합니다.")
    if post.author_id != request_user.id:
        raise PermissionDenied("본인 글만 수정할 수 있습니다.")


def _apply_category_if_provided(
    post: Post, cat_raw: object, include_category_field: bool
) -> bool:
    """
    카테고리 필드는 요청에 'category' 키가 포함된 경우에만 반영.
    변경된 경우 True 반환.
    """
    if not include_category_field:
        return False

    # 비우기(null)
    if cat_raw is None or (isinstance(cat_raw, str) and cat_raw.strip() == ""):
        if post.category_id is not None:
            post.category = None
            return True
        return False

    if not isinstance(cat_raw, str):
        raise ValidationError({"category": "카테고리는 문자열이어야 합니다."})

    cat = cat_raw.strip()
    if cat not in CATEGORY_KOR_ALLOWED:
        raise ValidationError({"category": f"허용되지 않는 카테고리입니다. {CATEGORY_KOR_ALLOWED} 중 선택하세요."})

    try:
        pc = PostCategory.objects.get(name=cat)
    except PostCategory.DoesNotExist:
        raise ValidationError({"category": "존재하지 않는 카테고리입니다. (사전 등록 필요)"})

    if post.category_id != pc.id:
        post.category = pc
        return True
    return False


def _ensure_lengths_if_provided(title: Optional[str], content: Optional[str]) -> None:
    if title is not None:
        if not isinstance(title, str):
            raise ValidationError({"title": "문자열이어야 합니다."})
        t = title.strip()
        if len(t) < 1 or len(t) > 100:
            raise ValidationError({"title": "길이는 1~100자여야 합니다."})

    if content is not None:
        if not isinstance(content, str):
            raise ValidationError({"content": "문자열이어야 합니다."})
        c = content.strip()
        if len(c) < 1 or len(c) > 20000:
            raise ValidationError({"content": "길이는 1~20000자여야 합니다."})


@transaction.atomic
def patch_post(request, post_id: str) -> Response:
    """
    부분 수정(PATCH):
    - 허용 필드: title, content, category, image_delete, image
    - JSON 또는 multipart/form-data 모두 지원
    - JSON에서 image 키를 보내면 415(이미지 업로드는 multipart 필요)
    - 응답: {post_id, updated_at}
    """
    pk = id_from_public(post_id)

    try:
        post = _alive_qs().select_related("author", "category").get(pk=pk)
    except Post.DoesNotExist:
        raise NotFound("게시글을 찾을 수 없습니다.")

    _ensure_author_or_403(request.user, post)

    is_multipart = (request.content_type or "").lower().startswith("multipart/")
    data = request.data
    included_keys = set(data.keys())

    # JSON에서 image 키가 오면 스펙 위배 → 415
    if not is_multipart and "image" in included_keys:
        raise UnsupportedMediaType(media_type=request.content_type or "application/json")

    title = data.get("title", None)
    content = data.get("content", None)
    category_raw = data.get("category", None)
    image_delete_raw = data.get("image_delete", None)
    image_file = request.FILES.get("image") if is_multipart else None

    _ensure_lengths_if_provided(title, content)

    dirty = False

    if title is not None:
        t = title.strip()
        if post.title != t:
            post.title = t
            dirty = True

    if content is not None:
        c = content.strip()
        if post.content != c:
            post.content = c
            dirty = True

    # category (요청에 키가 포함되었을 때만 반영)
    if _apply_category_if_provided(post, category_raw, include_category_field=("category" in included_keys)):
        dirty = True

    # image_delete / image
    if image_delete_raw is not None:
        img_del = _parse_bool(image_delete_raw)
        if img_del:
            if post.image:
                post.image.delete(save=False)
                post.image = None
                dirty = True

    if image_file is not None:
        post.image = image_file
        dirty = True

    if dirty:
        post.save()  # auto_now=True로 updated_at 갱신

    return Response(
        {
            "post_id": post.public_id,  # base64 공개 ID
            "updated_at": post.updated_at.isoformat().replace("+00:00", "Z"),
        },
        status=status.HTTP_200_OK,
    )
